select count((select ListDraft filter .owner.id = <uuid>$uid));
