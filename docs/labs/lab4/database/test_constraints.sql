\set ON_ERROR_STOP on
BEGIN;
INSERT INTO users(id,email,password_hash,name,status) VALUES
 ('00000000-0000-4000-8000-000000000001','student@example.test','fixture-hash','Артём','active');
INSERT INTO folders(id,owner_id,name) VALUES
 ('10000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000001','Учёба');
INSERT INTO files(id,owner_id,folder_id,name,mime_type,size_bytes,status) VALUES
 ('20000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000001',
 '10000000-0000-4000-8000-000000000001','lab.txt','text/plain',64,'active');
DO $$ BEGIN
 BEGIN
  INSERT INTO quotas(user_id,total_bytes,used_bytes) VALUES('00000000-0000-4000-8000-000000000001',10,11);
  RAISE EXCEPTION 'FAIL quota invariant';
 EXCEPTION WHEN check_violation THEN RAISE NOTICE 'PASS quota invariant'; END;
 BEGIN
  INSERT INTO share_links(created_by,file_id,folder_id,token_hash,access_level)
  VALUES('00000000-0000-4000-8000-000000000001','20000000-0000-4000-8000-000000000001',
  '10000000-0000-4000-8000-000000000001',repeat('a',64),'view');
  RAISE EXCEPTION 'FAIL share target XOR';
 EXCEPTION WHEN check_violation THEN RAISE NOTICE 'PASS share target XOR'; END;
 BEGIN
  INSERT INTO folders(owner_id,name) VALUES('00000000-0000-4000-8000-000000000001','учёба');
  RAISE EXCEPTION 'FAIL sibling uniqueness';
 EXCEPTION WHEN unique_violation THEN RAISE NOTICE 'PASS sibling uniqueness'; END;
 BEGIN
  INSERT INTO comments(file_id,author_id,text) VALUES('20000000-0000-4000-8000-999999999999',
  '00000000-0000-4000-8000-000000000001','test');
  RAISE EXCEPTION 'FAIL foreign key';
 EXCEPTION WHEN foreign_key_violation THEN RAISE NOTICE 'PASS foreign key'; END;
 BEGIN
  UPDATE files SET status='trashed' WHERE id='20000000-0000-4000-8000-000000000001';
  RAISE EXCEPTION 'FAIL trash timestamp';
 EXCEPTION WHEN check_violation THEN RAISE NOTICE 'PASS trash timestamp'; END;
 BEGIN
  INSERT INTO access_requests(user_id,type,reason,requested_role,status,decided_by,decided_at)
  VALUES('00000000-0000-4000-8000-000000000001','role','need access','admin','rejected',
  '00000000-0000-4000-8000-000000000001',now());
  RAISE EXCEPTION 'FAIL rejection requires comment';
 EXCEPTION WHEN check_violation THEN RAISE NOTICE 'PASS rejection requires comment'; END;
END $$;
INSERT INTO folders(id,owner_id,parent_id,name) VALUES
 ('10000000-0000-4000-8000-000000000002','00000000-0000-4000-8000-000000000001',
 '10000000-0000-4000-8000-000000000001','Подпапка');
DO $$ BEGIN
 BEGIN
  UPDATE folders SET parent_id='10000000-0000-4000-8000-000000000002'
   WHERE id='10000000-0000-4000-8000-000000000001';
  RAISE EXCEPTION 'FAIL folder cycle';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='folder cycle' THEN RAISE NOTICE 'PASS folder cycle'; ELSE RAISE; END IF;
 END;
END $$;
INSERT INTO audit_records(action,entity_type) VALUES('Test','test');
DO $$ BEGIN
 BEGIN
  DELETE FROM audit_records;
  RAISE EXCEPTION 'FAIL audit append only';
 EXCEPTION WHEN raise_exception THEN
  IF SQLERRM='audit records are append only' THEN RAISE NOTICE 'PASS audit append only'; ELSE RAISE; END IF;
 END;
END $$;
SELECT count(*) AS physical_tables FROM information_schema.tables WHERE table_schema='public';
ROLLBACK;
