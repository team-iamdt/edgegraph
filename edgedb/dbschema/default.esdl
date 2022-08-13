module default {
  # Base Model for Define Essential Values
  abstract type BaseModel {
    overloaded required property id -> uuid {
      constraint exclusive;
      readonly := true;
      default := uuid_generate_v1mc();
    };

    required property created_at -> datetime;
    required property updated_at -> datetime;
    property deleted_at -> datetime;
    required property deleted -> bool {
      default := false;
    };

    index on (.created_at) {
      annotation title := "CreatedAt Index";
    };
  }

  type User extending BaseModel {
    # Email is unique.
    required property email -> str {
      constraint exclusive;
    };

    required property password -> str;

    required property name -> str {
      constraint min_len_value(3);
    };

    index on (.email) {
      annotation title := "Email Index";
    };
  }

  abstract link IdIndex {
    property id -> uuid;
  }

  # Define Memo and Comment Model
  type Memo extending BaseModel {
    required link created_by extending IdIndex -> User;
    multi link accessable_users extending IdIndex -> User;

    required property title -> str;
    required property content -> str;
    required property tags -> array<str> {
      default := <array<str>>[];
    };
  }

  type Comment extending BaseModel {
    required link created_by extending IdIndex -> User;
    required link memo extending IdIndex -> Memo;
    required property content -> str;
  }
}
