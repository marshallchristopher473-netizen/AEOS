-- AEOS MVP Database Design
-- Production-safe schema for the Intervention Intelligence Platform
-- Security notes:
-- 1. All tenant-scoped tables include tenant_id.
-- 2. All sensitive writes should be audited.
-- 3. Avoid storing raw secrets or unrestricted free-form AI content without review.

create extension if not exists "uuid-ossp";
create extension if not exists vector;

create type user_role as enum ('admin', 'case_manager', 'teacher', 'support_staff');
create type assessment_status as enum ('draft', 'active', 'completed', 'archived');
create type intervention_status as enum ('draft', 'active', 'monitoring', 'completed', 'archived');
create type recommendation_source as enum ('ai_generated', 'manual', 'imported');
create type audit_action as enum ('create', 'update', 'delete', 'view', 'export');

create table if not exists organizations (
  id uuid primary key default uuid_generate_v4(),
  name text not null,
  organization_type text not null default 'school',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists users (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  auth_user_id uuid unique,
  email text not null unique,
  full_name text not null,
  role user_role not null default 'teacher',
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists schools (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  name text not null,
  district_name text,
  state_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists students (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  school_id uuid references schools(id) on delete set null,
  student_number text,
  first_name text not null,
  last_name text not null,
  grade_level text,
  iep_status boolean not null default false,
  birth_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint uq_student_identifier unique (organization_id, student_number)
);

create table if not exists assessments (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  created_by uuid not null references users(id) on delete restrict,
  title text not null,
  assessment_type text not null,
  status assessment_status not null default 'draft',
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists assessment_results (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  assessment_id uuid not null references assessments(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  score numeric,
  performance_band text,
  summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists intervention_plans (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  created_by uuid not null references users(id) on delete restrict,
  title text not null,
  status intervention_status not null default 'draft',
  summary text,
  priority text not null default 'medium',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists intervention_actions (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  intervention_plan_id uuid not null references intervention_plans(id) on delete cascade,
  assigned_to uuid references users(id) on delete set null,
  action_type text not null,
  description text not null,
  status text not null default 'pending',
  due_date date,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists notes (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  author_id uuid not null references users(id) on delete restrict,
  content text not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists ai_recommendation_runs (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  student_id uuid not null references students(id) on delete cascade,
  created_by uuid not null references users(id) on delete restrict,
  source recommendation_source not null default 'ai_generated',
  request_context jsonb not null default '{}'::jsonb,
  model_response jsonb not null default '{}'::jsonb,
  is_reviewed boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id uuid primary key default uuid_generate_v4(),
  organization_id uuid not null references organizations(id) on delete cascade,
  entity_type text not null,
  entity_id uuid,
  action audit_action not null,
  performed_by uuid references users(id) on delete set null,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_users_organization_id on users(organization_id);
create index if not exists idx_schools_organization_id on schools(organization_id);
create index if not exists idx_students_organization_id on students(organization_id);
create index if not exists idx_students_school_id on students(school_id);
create index if not exists idx_assessments_student_id on assessments(student_id);
create index if not exists idx_assessment_results_assessment_id on assessment_results(assessment_id);
create index if not exists idx_intervention_plans_student_id on intervention_plans(student_id);
create index if not exists idx_intervention_actions_plan_id on intervention_actions(intervention_plan_id);
create index if not exists idx_notes_student_id on notes(student_id);
create index if not exists idx_ai_recommendations_student_id on ai_recommendation_runs(student_id);
create index if not exists idx_audit_logs_organization_id on audit_logs(organization_id);
create index if not exists idx_audit_logs_entity on audit_logs(entity_type, entity_id);

-- Security considerations:
-- - Keep tenant boundaries enforced at the application layer and via row-level security policies in Supabase where possible.
-- - Avoid storing raw secrets or unrestricted files in the database.
-- - Audit all mutations to sensitive entities such as students, assessments, intervention plans, and AI recommendations.
