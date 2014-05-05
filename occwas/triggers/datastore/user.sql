--
-- avrc_data/user -> pirc/user
--
-- Uses ``key`` to find the user in both databases since
-- the was reconciled from two data sources (phi/fia)
--

DROP FOREIGN TABLE IF EXISTS user_ext;


CREATE FOREIGN TABLE user_ext (
    id              INTEGER

  , key             VARCHAR NOT NULL
  , create_date     TIMESTAMP NOT NULL
  , modify_date     TIMESTAMP NOT NULL
)
SERVER trigger_target
OPTIONS (table_name 'user');


--
-- Helper function to find the user id in the new system using
-- the old system id number
--
CREATE OR REPLACE FUNCTION ext_user_id(id INTEGER) RETURNS SETOF integer AS $$
  BEGIN
    RETURN QUERY
      SELECT "user_ext".id
      FROM "user_ext"
      WHERE key = (SELECT "user".key FROM "user" WHERE "user".id = $1);
  END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION user_mirror() RETURNS TRIGGER AS $$
  BEGIN
    CASE TG_OP
      WHEN 'INSERT' THEN
        IF NOT EXISTS(SELECT 1 FROM user_ext WHERE key = NEW.key) THEN
          INSERT INTO user_ext
            (key, create_date, modify_date)
          VALUES (NEW.key, NEW.create_date, NEW.modify_date);
        END IF;
      WHEN 'DELETE' THEN
        DELETE FROM user_ext WHERE key = OLD.key;
      WHEN 'UPDATE' THEN
        UPDATE user_ext
        SET key = NEW.key
          , create_date = NEW.create_date
          , modify_date = NEW.modify_date
        WHERE key = OLD.key;
    END CASE;
    RETURN NULL;
  END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS user_mirror ON "user";


CREATE TRIGGER user_mirror AFTER INSERT OR UPDATE OR DELETE ON "user"
  FOR EACH ROW EXECUTE PROCEDURE user_mirror();

