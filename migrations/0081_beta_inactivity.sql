-- When the inactivity reminder went out (unix seconds); a visit after it starts a new spell.
ALTER TABLE users ADD COLUMN beta_reminded_at INTEGER;
-- Beta reminders are counted beside the other mail, as totals per day only.
CREATE TABLE account_mail_daily_v5 (
 day TEXT NOT NULL, purpose TEXT NOT NULL CHECK(purpose IN ('verify','reset','activity','welcome','news','beta')),
 accepted INTEGER NOT NULL DEFAULT 0, failed INTEGER NOT NULL DEFAULT 0, limited INTEGER NOT NULL DEFAULT 0,
 PRIMARY KEY(day,purpose)
);
INSERT INTO account_mail_daily_v5 SELECT day,purpose,accepted,failed,limited FROM account_mail_daily;
DROP TABLE account_mail_daily;
ALTER TABLE account_mail_daily_v5 RENAME TO account_mail_daily;
