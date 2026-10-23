-- PostgreSQL 16+. Physical model derived from the 16 entities of lab 3.
BEGIN;
CREATE TABLE users (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 email varchar(255) NOT NULL UNIQUE,
 password_hash text NOT NULL,
 name varchar(120) NOT NULL,
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','blocked')),
 locale varchar(10) NOT NULL DEFAULT 'ru',
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(email = lower(email))
);
CREATE TABLE roles (
 id smallint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 code varchar(20) NOT NULL UNIQUE,
 title varchar(60) NOT NULL
);
CREATE TABLE user_roles (
 user_id uuid REFERENCES users(id) ON DELETE CASCADE,
 role_id smallint REFERENCES roles(id) ON DELETE RESTRICT,
 PRIMARY KEY(user_id,role_id)
);
CREATE TABLE sessions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 token_hash char(64) NOT NULL UNIQUE,
 ip_address inet,
 expires_at timestamptz NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(expires_at>created_at)
);
CREATE TABLE folders (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 owner_id uuid NOT NULL REFERENCES users(id),
 parent_id uuid REFERENCES folders(id) ON DELETE RESTRICT,
 name varchar(255) NOT NULL CHECK(length(trim(name))>0 AND name !~ '[/\\]'),
 is_shared boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(id,owner_id),
 FOREIGN KEY(parent_id,owner_id) REFERENCES folders(id,owner_id),
 CHECK(parent_id IS DISTINCT FROM id)
);
CREATE UNIQUE INDEX folders_sibling_name ON folders(owner_id,parent_id,lower(name)) NULLS NOT DISTINCT;
CREATE TABLE files (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 owner_id uuid NOT NULL REFERENCES users(id),
 folder_id uuid,
 name varchar(255) NOT NULL CHECK(length(trim(name))>0 AND name !~ '[/\\]'),
 mime_type varchar(127) NOT NULL,
 size_bytes bigint NOT NULL CHECK(size_bytes>=0),
 checksum char(64),
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','active','quarantine','trashed')),
 trashed_at timestamptz,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(id,owner_id),
 FOREIGN KEY(folder_id,owner_id) REFERENCES folders(id,owner_id),
 CHECK((status='trashed')=(trashed_at IS NOT NULL))
);
CREATE INDEX files_owner_folder ON files(owner_id,folder_id,status);
CREATE INDEX files_name_search ON files(lower(name));
CREATE TABLE file_versions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 file_id uuid NOT NULL REFERENCES files(id) ON DELETE CASCADE,
 version_no integer NOT NULL CHECK(version_no>0),
 storage_key varchar(512) NOT NULL UNIQUE,
 size_bytes bigint NOT NULL CHECK(size_bytes>=0),
 checksum char(64) NOT NULL,
 created_by uuid NOT NULL REFERENCES users(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 comment text,
 UNIQUE(file_id,version_no)
);
CREATE TABLE share_links (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 file_id uuid REFERENCES files(id) ON DELETE CASCADE,
 folder_id uuid REFERENCES folders(id) ON DELETE CASCADE,
 token_hash char(64) NOT NULL UNIQUE,
 access_level varchar(10) NOT NULL CHECK(access_level IN ('view','download')),
 password_hash text,
 expires_at timestamptz,
 revoked_at timestamptz,
 download_limit integer CHECK(download_limit>0),
 downloads integer NOT NULL DEFAULT 0 CHECK(downloads>=0),
 created_by uuid NOT NULL REFERENCES users(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(num_nonnulls(file_id,folder_id)=1),
 CHECK(expires_at IS NULL OR expires_at>created_at),
 CHECK(download_limit IS NULL OR downloads<=download_limit)
);
CREATE TABLE access_permissions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 file_id uuid REFERENCES files(id) ON DELETE CASCADE,
 folder_id uuid REFERENCES folders(id) ON DELETE CASCADE,
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 level varchar(10) NOT NULL CHECK(level IN ('view','edit')),
 granted_at timestamptz NOT NULL DEFAULT now(),
 CHECK(num_nonnulls(file_id,folder_id)=1)
);
CREATE UNIQUE INDEX permissions_file ON access_permissions(file_id,user_id) WHERE file_id IS NOT NULL;
CREATE UNIQUE INDEX permissions_folder ON access_permissions(folder_id,user_id) WHERE folder_id IS NOT NULL;
CREATE TABLE folder_members (
 folder_id uuid REFERENCES folders(id) ON DELETE CASCADE,
 user_id uuid REFERENCES users(id) ON DELETE CASCADE,
 role varchar(10) NOT NULL CHECK(role IN ('view','edit')),
 invited_at timestamptz NOT NULL DEFAULT now(),
 PRIMARY KEY(folder_id,user_id)
);
CREATE TABLE invitations (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 folder_id uuid NOT NULL REFERENCES folders(id) ON DELETE CASCADE,
 email varchar(255) NOT NULL,
 token_hash char(64) NOT NULL UNIQUE,
 level varchar(10) NOT NULL CHECK(level IN ('view','edit')),
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','expired','revoked')),
 expires_at timestamptz NOT NULL,
 invited_by uuid NOT NULL REFERENCES users(id),
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK(expires_at>created_at)
);
CREATE TABLE access_requests (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES users(id),
 type varchar(20) NOT NULL CHECK(type IN ('quota','role')),
 reason text NOT NULL CHECK(length(trim(reason))>0),
 requested_bytes bigint CHECK(requested_bytes>0),
 requested_role varchar(20),
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
 decided_by uuid REFERENCES users(id),
 decided_at timestamptz,
 decision_comment text,
 created_at timestamptz NOT NULL DEFAULT now(),
 CHECK((status='pending' AND decided_by IS NULL AND decided_at IS NULL) OR
       (status<>'pending' AND decided_by IS NOT NULL AND decided_at IS NOT NULL)),
 CHECK(status<>'rejected' OR COALESCE(length(trim(decision_comment)),0)>0),
 CHECK((type='quota' AND requested_bytes IS NOT NULL AND requested_role IS NULL) OR
       (type='role' AND requested_role IS NOT NULL AND requested_bytes IS NULL))
);
CREATE INDEX access_requests_queue ON access_requests(status,created_at);
CREATE TABLE quotas (
 user_id uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
 used_bytes bigint NOT NULL DEFAULT 0 CHECK(used_bytes>=0),
 total_bytes bigint NOT NULL DEFAULT 16106127360 CHECK(total_bytes>=0),
 reserved_bytes bigint NOT NULL DEFAULT 0 CHECK(reserved_bytes>=0),
 tariff varchar(40) NOT NULL DEFAULT 'free',
 renewal_date date,
 CHECK(used_bytes+reserved_bytes<=total_bytes)
);
CREATE TABLE audit_records (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 user_id uuid REFERENCES users(id),
 action varchar(80) NOT NULL,
 entity_type varchar(40) NOT NULL,
 entity_id uuid,
 ip_address inet,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX audit_records_time ON audit_records(created_at DESC);
CREATE TABLE notifications (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 type varchar(40) NOT NULL,
 text text NOT NULL,
 is_read boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX notifications_unread ON notifications(user_id,created_at DESC) WHERE NOT is_read;
CREATE TABLE comments (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 file_id uuid NOT NULL REFERENCES files(id) ON DELETE CASCADE,
 author_id uuid NOT NULL REFERENCES users(id),
 text text NOT NULL CHECK(length(trim(text)) BETWEEN 1 AND 5000),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX comments_file ON comments(file_id,created_at);
-- Upload sessions extend the logical model to support resume and idempotent completion.
CREATE TABLE upload_sessions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id uuid NOT NULL REFERENCES users(id),
 file_id uuid REFERENCES files(id),
 expected_bytes bigint NOT NULL CHECK(expected_bytes>0),
 received_bytes bigint NOT NULL DEFAULT 0 CHECK(received_bytes>=0),
 idempotency_key uuid NOT NULL,
 status varchar(20) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','completed','cancelled')),
 expires_at timestamptz NOT NULL,
 UNIQUE(user_id,idempotency_key),
 CHECK(received_bytes<=expected_bytes)
);
-- Application transactions must reserve quota, verify ACL, and validate folder cycles.
CREATE FUNCTION prevent_folder_cycle() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.parent_id IS NOT NULL AND EXISTS (
   WITH RECURSIVE ancestors AS (
     SELECT id,parent_id FROM folders WHERE id=NEW.parent_id
     UNION SELECT f.id,f.parent_id FROM folders f JOIN ancestors a ON f.id=a.parent_id
   ) SELECT 1 FROM ancestors WHERE id=NEW.id
 ) THEN RAISE EXCEPTION 'folder cycle'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER folder_no_cycles BEFORE INSERT OR UPDATE OF parent_id ON folders
 FOR EACH ROW EXECUTE FUNCTION prevent_folder_cycle();
CREATE FUNCTION audit_immutable() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'audit records are append only'; END $$;
CREATE TRIGGER audit_no_change BEFORE UPDATE OR DELETE ON audit_records
 FOR EACH ROW EXECUTE FUNCTION audit_immutable();
INSERT INTO roles(code,title) VALUES('user','Пользователь'),('admin','Администратор');
COMMIT;
