# Логическая схема базы данных

Модель продолжает 16 сущностей ЛР3. Добавлена upload_sessions для загрузки частями и идемпотентного завершения. Содержимое файлов хранится в S3, в таблицах остаются метаданные.

## users

`id` (PK), `email`, `password_hash`, `name`, `status`, `locale`, `created_at`.

## roles

`id` (PK), `code`, `title`.

## user_roles

`user_id` (PK,FK), `role_id` (PK,FK).

## sessions

`id` (PK), `user_id` (FK), `token_hash`, `ip_address`, `expires_at`, `created_at`.

## folders

`id` (PK), `owner_id` (FK), `parent_id` (FK), `name`, `is_shared`, `created_at`.

## files

`id` (PK), `owner_id` (FK), `folder_id` (FK), `name`, `mime_type`, `size_bytes`, `checksum`, `status`, `trashed_at`, `created_at`.

## file_versions

`id` (PK), `file_id` (FK), `version_no`, `storage_key`, `size_bytes`, `checksum`, `created_by` (FK), `created_at`, `comment`.

## share_links

`id` (PK), `file_id` (FK), `folder_id` (FK), `token_hash`, `access_level`, `password_hash`, `expires_at`, `revoked_at`, `download_limit`, `downloads`, `created_by` (FK), `created_at`.

## access_permissions

`id` (PK), `file_id` (FK), `folder_id` (FK), `user_id` (FK), `level`, `granted_at`.

## folder_members

`folder_id` (PK,FK), `user_id` (PK,FK), `role`, `invited_at`.

## invitations

`id` (PK), `folder_id` (FK), `email`, `token_hash`, `level`, `status`, `expires_at`, `invited_by` (FK), `created_at`.

## access_requests

`id` (PK), `user_id` (FK), `type`, `reason`, `requested_bytes`, `requested_role`, `status`, `decided_by` (FK), `decided_at`, `decision_comment`, `created_at`.

## quotas

`user_id` (PK,FK), `used_bytes`, `total_bytes`, `reserved_bytes`, `tariff`, `renewal_date`.

## audit_records

`id` (PK), `user_id` (FK), `action`, `entity_type`, `entity_id`, `ip_address`, `created_at`.

## notifications

`id` (PK), `user_id` (FK), `type`, `text`, `is_read`, `created_at`.

## comments

`id` (PK), `file_id` (FK), `author_id` (FK), `text`, `created_at`.

## upload_sessions

`id` (PK), `user_id` (FK), `file_id` (FK), `expected_bytes`, `received_bytes`, `idempotency_key`, `status`, `expires_at`.

## Связи

files.id → access_permissions.file_id (1:N).

files.id → comments.file_id (1:N).

files.id → file_versions.file_id (1:N).

files.id → share_links.file_id (1:N).

files.id → upload_sessions.file_id (1:N).

folders.id → access_permissions.folder_id (1:N).

folders.id → files.folder_id (1:N).

folders.id → folder_members.folder_id (1:N).

folders.id → folders.parent_id (1:N).

folders.id → invitations.folder_id (1:N).

folders.id → share_links.folder_id (1:N).

roles.id → user_roles.role_id (1:N).

users.id → access_permissions.user_id (1:N).

users.id → access_requests.decided_by (1:N).

users.id → access_requests.user_id (1:N).

users.id → audit_records.user_id (1:N).

users.id → comments.author_id (1:N).

users.id → file_versions.created_by (1:N).

users.id → files.owner_id (1:N).

users.id → folder_members.user_id (1:N).

users.id → folders.owner_id (1:N).

users.id → invitations.invited_by (1:N).

users.id → notifications.user_id (1:N).

users.id → quotas.user_id (1:0..1).

users.id → sessions.user_id (1:N).

users.id → share_links.created_by (1:N).

users.id → upload_sessions.user_id (1:N).

users.id → user_roles.user_id (1:N).

