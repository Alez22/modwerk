/* SPDX-License-Identifier: MIT */
/* Original small lettering, extended from the private planner probe. */
#include "device_font.h"
static const unsigned char letters[26][7]={
 {14,17,17,31,17,17,17},{30,17,17,30,17,17,30},{14,17,16,16,16,17,14},
 {30,17,17,17,17,17,30},{31,16,16,30,16,16,31},{31,16,16,30,16,16,16},
 {14,17,16,23,17,17,14},{17,17,17,31,17,17,17},{31,4,4,4,4,4,31},
 {1,1,1,1,17,17,14},{17,18,20,24,20,18,17},{16,16,16,16,16,16,31},
 {17,27,21,21,17,17,17},{17,25,21,19,17,17,17},{14,17,17,17,17,17,14},
 {30,17,17,30,16,16,16},{14,17,17,17,21,18,13},{30,17,17,30,20,18,17},
 {15,16,16,14,1,1,30},{31,4,4,4,4,4,4},{17,17,17,17,17,17,14},
 {17,17,17,17,17,10,4},{17,17,17,21,21,21,10},{17,17,10,4,10,17,17},
 {17,17,10,4,4,4,4},{31,1,2,4,8,16,31}
};
static const unsigned char digits[10][7]={
 {14,17,19,21,25,17,14},{4,12,4,4,4,4,14},{14,17,1,2,4,8,31},
 {30,1,1,14,1,1,30},{2,6,10,18,31,2,2},{31,16,16,30,1,1,30},
 {14,16,16,30,17,17,14},{31,1,2,4,8,8,8},{14,17,17,14,17,17,14},
 {14,17,17,15,1,1,14}
};
void bs_device_text(unsigned char *frame,uint32_t y,const char *s){
 if(!frame || !s || y>57)return;
 for(uint32_t x=4;*s && x+5<=128;x+=6,++s){
  const unsigned char *glyph=0;
  if(*s>='A' && *s<='Z')glyph=letters[(unsigned)*s-'A'];
  if(*s>='0' && *s<='9')glyph=digits[(unsigned)*s-'0'];
  for(uint32_t row=0;row<7;++row){
   uint32_t bits=glyph?glyph[row]:0;
   if(*s==':' && (row==2 || row==5))bits=4;
   if(*s=='.' && row==6)bits=4;
   if(*s=='-' && row==3)bits=14;
   for(uint32_t column=0;column<5;++column)if(bits&(16u>>column))
    frame[(x+column)*8u+7u-(y+row)/8u]|=(unsigned char)(1u<<((y+row)%8u));
  }
 }
}
