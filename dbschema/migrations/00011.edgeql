CREATE MIGRATION m1sdtnf3q4wiucpjosaxvjvp74vkkjghjg5d6uvocjld4xcxthzbkq
    ONTO m1oviite3rv5e4bydyxcmgxn3f2lxgvftk4tewqrlie5mg6h6dvboq
{
  ALTER TYPE default::ItemDraft EXTENDING default::Auditable,
  default::Editable LAST;
  ALTER TYPE default::ListDraft EXTENDING default::Auditable,
  default::Editable LAST;
};
