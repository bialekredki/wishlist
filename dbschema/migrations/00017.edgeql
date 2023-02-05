CREATE MIGRATION m1rxh6lmb7xua6zzr6a7wrymchspchey5ws4clme654effb4z7sera
    ONTO m1dyxpx5n2gheachkvdqsmo6pagvvhfg76hy2cpeb33qowimx3c2vq
{
  ALTER TYPE default::ListDraft {
      CREATE PROPERTY active_list_slug := (.active_list.slug);
  };
};
