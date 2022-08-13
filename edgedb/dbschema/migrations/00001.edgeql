CREATE MIGRATION m1q7lx3uun4deovuv7tneexfhwjl5kerzjqzmksy3crbad25ws4yxa
    ONTO initial
{
  CREATE ABSTRACT LINK default::IdIndex {
      CREATE PROPERTY id -> std::uuid;
  };
  CREATE ABSTRACT TYPE default::BaseModel {
      CREATE REQUIRED PROPERTY created_at -> std::datetime;
      CREATE REQUIRED PROPERTY deleted -> std::bool {
          SET default := false;
      };
      CREATE PROPERTY deleted_at -> std::datetime;
      ALTER PROPERTY id {
          SET default := (std::uuid_generate_v1mc());
          SET OWNED;
          SET readonly := true;
          SET REQUIRED;
          SET TYPE std::uuid;
          ALTER CONSTRAINT std::exclusive {
              SET OWNED;
          };
      };
      CREATE REQUIRED PROPERTY updated_at -> std::datetime;
      CREATE INDEX ON (.created_at) {
          CREATE ANNOTATION std::title := 'CreatedAt Index';
      };
  };
  CREATE TYPE default::User EXTENDING default::BaseModel {
      CREATE REQUIRED PROPERTY email -> std::str {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE INDEX ON (.email) {
          CREATE ANNOTATION std::title := 'Email Index';
      };
      CREATE REQUIRED PROPERTY name -> std::str {
          CREATE CONSTRAINT std::min_len_value(3);
      };
      CREATE REQUIRED PROPERTY password -> std::str;
  };
  CREATE TYPE default::Memo EXTENDING default::BaseModel {
      CREATE MULTI LINK accessable_users EXTENDING default::IdIndex -> default::User;
      CREATE REQUIRED LINK created_by EXTENDING default::IdIndex -> default::User;
      CREATE REQUIRED PROPERTY content -> std::str;
      CREATE REQUIRED PROPERTY tags -> array<std::str> {
          SET default := (<array<std::str>>[]);
      };
      CREATE REQUIRED PROPERTY title -> std::str;
  };
  CREATE TYPE default::Comment EXTENDING default::BaseModel {
      CREATE REQUIRED LINK created_by EXTENDING default::IdIndex -> default::User;
      CREATE REQUIRED LINK memo EXTENDING default::IdIndex -> default::Memo;
      CREATE REQUIRED PROPERTY content -> std::str;
  };
};
