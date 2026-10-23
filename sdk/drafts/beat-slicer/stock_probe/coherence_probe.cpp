// SPDX-License-Identifier: MIT
// Original synthetic pool fixtures; private hash-bound stock supplied at runtime.
// No project, filesystem, scheduler, DSP or device runs. No callees are mocked.
#include <algorithm>
#include <array>
#include <cstdio>
#include <fstream>
#include <iterator>
#include <stdexcept>
#include <vector>
#include "machine.h"
#include "mc68k/Musashi/m68k.h"
#include "mc68k/cpuState.h"
extern "C" {
#include "../pcm_reader.h"
}
namespace {
constexpr uint32_t stack = 0x47100000, stop = 0x47300000;
constexpr uint32_t pool = 0x40a955e0, pageBytes = 6144;
constexpr uint32_t controls = 0x46c922c4, dirty = 0x46c93c28;
constexpr uint32_t pageList = 0x46c2e9c0, offsets = 0x46c2e580, counts = 0x46c75e88;
constexpr std::array<unsigned, 3> pages{3, 7, 2};
constexpr std::array<m68k_register_t, 11> saved{
    M68K_REG_D2, M68K_REG_D3, M68K_REG_D4, M68K_REG_D5, M68K_REG_D6,
    M68K_REG_D7, M68K_REG_A2, M68K_REG_A3, M68K_REG_A4, M68K_REG_A5, M68K_REG_A6};
void require(bool ok, const char* msg) { if (!ok) throw std::runtime_error(msg); }
struct Probe {
    ot::Machine m;
    explicit Probe(const std::vector<uint8_t>& image) : m(image) {}
    uint32_t reg(m68k_register_t r) { return m68k_get_reg(m.getCpuState(), r); }
    void reg(m68k_register_t r, uint32_t v) { m68k_set_reg(m.getCpuState(), r, v); }
    uint32_t run(uint32_t entry, std::initializer_list<uint32_t> args) {
        reg(M68K_REG_SR, 0x2700); reg(M68K_REG_SP, stack); m.write32(stack, stop);
        for (unsigned i = 0; i < saved.size(); ++i) reg(saved[i], 0x12340000+i);
        unsigned i = 0;
        for (auto a : args) m.write32(stack+4+4*i++, a);
        reg(M68K_REG_PC, entry);
        unsigned steps = 0;
        while (m.pc() != stop && ++steps < 2000000)
            if (!m.step()) throw std::runtime_error("CPU stopped: " + m.why());
        require(m.pc() == stop && reg(M68K_REG_SP) == stack+4, "return/budget differs");
        require(reg(M68K_REG_SR) >> 8 == 0x27, "interrupt mask not restored");
        for (unsigned n = 0; n < saved.size(); ++n)
            require(reg(saved[n]) == 0x12340000+n, "callee-saved register changed");
        return reg(M68K_REG_D0);
    }
    std::vector<uint8_t> bytes(uint32_t at, unsigned size) {
        std::vector<uint8_t> v(size);
        for (unsigned i = 0; i < size; ++i) v[i] = m.read8(at+i);
        return v;
    }
    unsigned width(unsigned format) { return (format & 2 ? 2 : 3) * (format & 1 ? 2 : 1); }
    uint32_t address(unsigned format, unsigned frame) {
        unsigned framesPerPage = pageBytes/width(format);
        return pool + pages[frame/framesPerPage]*pageBytes + frame%framesPerPage*width(format);
    }
    static int32_t value(unsigned frame, unsigned channel) {
        return channel ? (int32_t(frame%17)-8)*512 : (int32_t(frame%31)-15)*256;
    }
    int32_t sample(unsigned format, unsigned frame, unsigned channel) {
        unsigned n = format & 2 ? 2 : 3;
        uint32_t at = address(format, frame)+channel*n, v = 0;
        for (unsigned b = 0; b < n; ++b) v = (v << 8) | m.read8(at+b);
        int32_t signedValue = int32_t(v) - (v & (1u << (8*n-1)) ? int32_t(1u << (8*n)) : 0);
        return n == 2 ? signedValue*256 : signedValue;
    }
    void setup(unsigned format, unsigned length) {
        m.write32(0x46105408, 1);
        m.write32(controls, format); m.write32(controls+8, 0);
        m.write32(controls+16, length); m.write32(controls+20, 41);
        m.write8(dirty, 0);
        // Authored descriptor geometry, never extracted stock table contents.
        m.write32(0x80003c20+16*format+4, pageBytes/width(format));
        m.write32(0x80003c20+16*format+8, width(format));
        m.write32(0x80006914, pageList); m.write32(0x80006918, offsets);
        m.write32(offsets, 0);
        m.write16(counts, uint16_t((length*width(format)+pageBytes-1)/pageBytes));
        for (unsigned i = 0; i < pages.size(); ++i) {
            m.write16(pageList+2*i, pages[i]);
            for (unsigned b = 0; b < pageBytes; ++b) m.write8(pool+pages[i]*pageBytes+b, 0x5a);
        }
        unsigned sampleBytes = format & 2 ? 2 : 3;
        for (unsigned frame = 0; frame < length; ++frame)
            for (unsigned ch = 0; ch < (format & 1 ? 2u : 1u); ++ch) {
                uint32_t v = uint32_t(value(frame, ch));
                if (sampleBytes == 2) v >>= 8;
                for (unsigned b = 0; b < sampleBytes; ++b)
                    m.write8(address(format, frame)+ch*sampleBytes+b, v >> (8*(sampleBytes-1-b)));
            }
    }
};
void inversion(const std::vector<uint8_t>& image) {
    for (unsigned format : {1u, 3u}) for (unsigned mode = 0; mode < 3; ++mode) {
        Probe p(image);
        const unsigned boundary = pageBytes/p.width(format), length = boundary+3;
        p.setup(format, length);
        const auto controlBefore = p.bytes(controls, 44);
        // Repeat the edit: dirty is already set on the second operation.
        for (unsigned repeat = 0; repeat < 2; ++repeat) {
            require(p.run(0x40094c94, {0, boundary-1, boundary+2, mode}) == 1, "invert refused");
            require(p.bytes(controls, 44) == controlBefore, "invert changed control metadata");
            require(p.m.read8(dirty) == 255, "invert dirty flag differs");
            for (unsigned frame = 0; frame < length; ++frame) for (unsigned ch = 0; ch < 2; ++ch) {
                bool invert = !repeat && frame >= boundary-1 && frame < boundary+2 &&
                              (mode == 2 || mode == ch);
                auto expected = Probe::value(frame, ch) * (invert ? -1 : 1);
                require(p.sample(format, frame, ch) == expected, "invert PCM differs");
            }
        }
    }
}
void rotation(const std::vector<uint8_t>& image) {
    for (unsigned format = 0; format < 4; ++format) {
        Probe p(image); p.setup(format, 17);
        const auto controlBefore = p.bytes(controls, 44);
        for (unsigned repeat = 1; repeat <= 2; ++repeat) {
            require(p.run(0x40094b6c, {0, 3}) == 1, "rotate refused");
            require(p.bytes(controls, 44) == controlBefore, "rotate changed control metadata");
            require(p.m.read8(dirty) == 255, "rotate dirty flag differs");
            for (unsigned frame = 0; frame < 17; ++frame)
                for (unsigned ch = 0; ch < (format & 1 ? 2u : 1u); ++ch)
                    require(p.sample(format, frame, ch) == Probe::value((frame+3*repeat)%17, ch),
                            "rotate PCM differs");
        }
    }
}
void refusals(const std::vector<uint8_t>& image) {
    for (unsigned test = 0; test < 8; ++test) {
        Probe p(image); p.setup(test == 0 ? 2 : 3, 17);
        unsigned slot = 0, first = 0, end = 17;
        uint32_t expected = uint32_t(-2);
        switch (test) {
        case 1: p.m.write32(controls+8, 1); expected = uint32_t(-3); break;
        case 2: p.m.write32(0x46105408, 0); break;
        case 3: slot = 136; break;
        case 4: first = UINT32_MAX; break;
        case 5: end = 18; break;
        case 6: end = first; break;
        case 7: first = 9; end = 8; break;
        }
        const auto before = p.bytes(pool, 8*pageBytes), meta = p.bytes(controls, 44);
        require(p.run(0x40094c94, {slot, first, end, 2}) == expected, "refusal code differs");
        require(p.bytes(pool, 8*pageBytes) == before && p.bytes(controls, 44) == meta &&
                p.m.read8(dirty) == 0, "refused edit changed source/state");
    }
}
void release(const std::vector<uint8_t>& image) {
    for (uint32_t generation : {0u, 41u, UINT32_MAX}) {
        Probe p(image); p.setup(3, pageBytes/4+3);
        p.m.write32(controls+20, generation);
        p.m.write32(0x8000691c, 3); p.m.write32(0x80006920, 14602);
        // A second loaded slot owns one page after the released two-page slot.
        const unsigned other = 127, otherControl = controls+44*other;
        p.m.write32(offsets+4*other, 2); p.m.write16(counts+2*other, 1);
        p.m.write32(otherControl, 3); p.m.write32(otherControl+8, 0);
        p.m.write32(otherControl+16, 10); p.m.write32(otherControl+20, 99);
        const auto otherBefore = p.bytes(otherControl, 44);
        const auto audioBefore = p.bytes(pool+pages[2]*pageBytes, pageBytes);
        std::vector<uint32_t> maps;
        p.m.addWriteWatch(0x80006914, 0x8000691b, [&](uint32_t at, uint8_t, uint32_t v, uint32_t) {
            if (at == 0x80006914) maps.push_back(v);
        });
        p.run(0x40096300, {0});
        require(p.m.read32(controls+20) == (generation == UINT32_MAX ? 1 : generation+1),
                "release counter/wrap differs");
        require(p.m.read32(controls+8) == 1 && p.m.read32(controls+16) == 0 &&
                p.m.read16(counts) == 0 && p.m.read8(dirty) == 0, "release state differs");
        for (unsigned page : {pages[0], pages[1]}) {
            auto cleared = p.bytes(pool+page*pageBytes, pageBytes);
            require(std::all_of(cleared.begin(), cleared.end(), [](uint8_t b) { return b == 0; }),
                    "released audio not cleared");
        }
        require(p.m.read32(offsets+4*other) == 0 && p.m.read16(pageList) == pages[2] &&
                p.m.read32(0x8000691c) == 1, "survivor allocation map differs");
        require(p.bytes(otherControl, 44) == otherBefore &&
                p.bytes(pool+pages[2]*pageBytes, pageBytes) == audioBefore, "survivor changed");
        require(maps == std::vector<uint32_t>{0x46c35bd4, pageList}, "temporary map publication differs");
        require(p.run(0x4009499c, {other, 0, 1}) == pool+pages[2]*pageBytes, "survivor read differs");
    }
}
int referenceFrame(void* context, uint32_t frame, int32_t out[2]) {
    unsigned format = *static_cast<unsigned*>(context);
    out[0] = Probe::value(frame, 0);
    out[1] = format & 1 ? Probe::value(frame, 1) : out[0];
    return 0;
}
bool samePlan(const bs_plan& a, const bs_plan& b) {
    if (a.count != b.count || a.bpm24 != b.bpm24 || a.end_needs_fade != b.end_needs_fade) return false;
    for (unsigned i = 0; i < BS_MAX_SLICES; ++i)
        if (a.starts[i] != b.starts[i] || a.needs_fade[i] != b.needs_fade[i]) return false;
    return true;
}
void pipeline(const std::vector<uint8_t>& image) {
    for (unsigned format = 0; format < 4; ++format) for (unsigned snap = 0; snap < 2; ++snap) {
        Probe p(image);
        const unsigned length = 2*pageBytes/p.width(format)+17;
        p.setup(format, length);
        const auto before = p.bytes(pool, 8*pageBytes), metadata = p.bytes(controls, 44);
        bs_request request{};
        request.sample_rate = 8000; request.trim_start = 0; request.trim_end = length;
        request.sample_bpm24 = 7200; request.beats = 1; request.snap = snap;
        request.read = referenceFrame; request.context = &format;
        bs_plan expected{}, actual{};
        require(bs_preview(&request, &expected) == BS_OK, "reference preview failed");
        // The epoch is authored by this isolated provider, NOT read from the
        // stock control counter. There are no concurrent writers in this test.
        bs_pcm_source source{1, 2, length, {format & 2 ? 16u : 24u, format & 1 ? 2u : 1u, 0}};
        bs_pcm_reader reader{};
        require(bs_reader_begin(&reader, &request, &source) == BS_READER_RUNNING, "reader refused fixture");
        unsigned ticks = 0, reads = 0;
        bs_reader_state st;
        while ((st = bs_reader_step(&reader, source.revision)) < BS_READER_DONE) {
            require(++ticks < 20000, "reader budget exhausted");
            if (st != BS_READER_NEED_BLOCK) continue;
            auto pointer = p.run(0x4009499c, {0, reader.pending.first, 1});
            const unsigned count = std::min(reader.pending.count, p.reg(M68K_REG_D1));
            require(count > 0 && count <= BS_PCM_BLOCK_FRAMES, "stock returned invalid page extent");
            auto packed = p.bytes(pointer, count*p.width(format));
            require(bs_reader_supply(&reader, &reader.pending, packed.data(), packed.size(), 0), "reply refused");
            ++reads;
        }
        require(reads > 0 && st == BS_READER_DONE && bs_reader_result(&reader, source.revision, &actual) &&
                samePlan(expected, actual), "stock-page preview differs from formula oracle");
        require(p.bytes(pool, 8*pageBytes) == before && p.bytes(controls, 44) == metadata &&
                p.m.read8(dirty) == 0, "preview changed stock fixture");
        // The provider must invalidate even completed previews before exposing
        // them after a real content mutation. Stock's counter stays at 41.
        require(p.run(0x40094b6c, {0, 3}) == 1 && p.m.read32(controls+20) == 41,
                "post-preview edit fixture differs");
        actual.count = 123;
        require(!bs_reader_result(&reader, ++source.revision, &actual) && actual.count == 123 &&
                reader.job.state == BS_JOB_FAILED, "invalidated completed preview escaped");
    }
}
} // namespace
int main(int argc, char** argv) {
    std::printf("SOURCE_SHA256: %s\n", PROBE_SOURCE_SHA);
    if (argc != 2) return 2;
    std::ifstream in(argv[1], std::ios::binary);
    std::vector<uint8_t> image{std::istreambuf_iterator<char>(in), {}};
    if (image.size() != 1112560) return 2;
    const std::pair<const char*, void (*)(const std::vector<uint8_t>&)> cases[] = {
        {"12 stereo inversions across page boundaries leave control counter unchanged and dirty sticky", inversion},
        {"eight rotations across four formats leave control counter unchanged and dirty sticky", rotation},
        {"eight unsupported/busy/range refusals preserve source and metadata", refusals},
        {"three pool releases: counter wrap, clearing, temporary maps and survivor isolation", release},
        {"eight stock-page to host-reader previews and explicit post-edit invalidation", pipeline},
    };
    unsigned failed = 0;
    for (const auto& c : cases) {
        try { c.second(image); std::printf("PASS: %s\n", c.first); }
        catch (const std::exception& e) { ++failed; std::printf("FAIL: %s: %s\n", c.first, e.what()); }
    }
    std::printf("%u passed, %u failed; isolated synthetic pool, no concurrent scheduler or hardware\n", 5-failed, failed);
    return failed ? 1 : 0;
}
