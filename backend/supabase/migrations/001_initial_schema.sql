CREATE TYPE organization_type AS ENUM ('district', 'school', 'pilot');
CREATE TYPE organization_status AS ENUM ('active', 'suspended');
CREATE TYPE school_status AS ENUM ('active', 'inactive');
CREATE TYPE user_role AS ENUM ('teacher', 'admin', 'support');
CREATE TYPE user_status AS ENUM ('active', 'disabled');
CREATE TYPE student_status AS ENUM ('active', 'inactive');
CREATE TYPE assessment_status AS ENUM ('draft', 'submitted', 'in_review', 'complete');
CREATE TYPE recommendation_status AS ENUM ('generated', 'reviewed', 'accepted', 'rejected');
CREATE TYPE intervention_plan_status AS ENUM ('draft', 'active', 'completed', 'archived');
CREATE TYPE intervention_action_status AS ENUM ('pending', 'in_progress', 'completed');
CREATE TYPE progress_event_type AS ENUM (
    'student_created',
    'assessment_created',
    'assessment_updated',
    'recommendation_generated',
    'recommendation_reviewed',
    'intervention_created',
    'intervention_updated',
    'progress_logged'
);

CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    type organization_type NOT NULL,
    status organization_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE schools (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    district_name TEXT,
    status school_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT schools_name_org_unique UNIQUE (organization_id, name)
);

CREATE TABLE users (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    auth_user_id TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role user_role NOT NULL,
    status user_status NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT users_auth_user_unique UNIQUE (organization_id, auth_user_id)
);

CREATE TABLE students (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    school_id UUID REFERENCES schools(id) ON DELETE SET NULL,
    student_number TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    grade_level TEXT,
    iep_status BOOLEAN NOT NULL DEFAULT FALSE,
    birth_date DATE,
    status student_status NOT NULL DEFAULT 'active',
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT students_org_student_number_unique UNIQUE (organization_id, student_number)
);

CREATE TABLE assessments (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    status assessment_status NOT NULL DEFAULT 'draft',
    notes TEXT,
    response_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    model_name TEXT NOT NULL,
    prompt_summary TEXT,
    recommendation_text TEXT NOT NULL,
    confidence_score NUMERIC(5,4),
    status recommendation_status NOT NULL DEFAULT 'generated',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE intervention_plans (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE SET NULL,
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    status intervention_plan_status NOT NULL DEFAULT 'draft',
    summary TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE intervention_actions (
    id UUID PRIMARY KEY,
    intervention_plan_id UUID NOT NULL REFERENCES intervention_plans(id) ON DELETE CASCADE,
    action_type TEXT NOT NULL,
    description TEXT NOT NULL,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    due_date DATE,
    status intervention_action_status NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE progress_events (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    actor_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    event_type progress_event_type NOT NULL,
    event_message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL,
    entity_id UUID NOT NULL,
    action TEXT NOT NULL,
    performed_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Future-proofing: placeholder columns for upcoming modules
ALTER TABLE students ADD COLUMN iep_id UUID;
ALTER TABLE assessments ADD COLUMN standard_id UUID;
ALTER TABLE intervention_plans ADD COLUMN evidence_summary JSONB;

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER organizations_set_updated_at
BEFORE UPDATE ON organizations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER schools_set_updated_at
BEFORE UPDATE ON schools
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER students_set_updated_at
BEFORE UPDATE ON students
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER assessments_set_updated_at
BEFORE UPDATE ON assessments
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER ai_recommendations_set_updated_at
BEFORE UPDATE ON ai_recommendations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER intervention_plans_set_updated_at
BEFORE UPDATE ON intervention_plans
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER intervention_actions_set_updated_at
BEFORE UPDATE ON intervention_actions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO organizations (
    id,
    name,
    type,
    status,
    created_at,
    updated_at
) VALUES (
    '11111111-1111-4111-8111-111111111111',
    'Demo District',
    'district',
    'active',
    NOW(),
    NOW()
);

INSERT INTO schools (
    id,
    organization_id,
    name,
    district_name,
    status,
    created_at,
    updated_at
) VALUES (
    '22222222-2222-4222-8222-222222222222',
    '11111111-1111-4111-8111-111111111111',
    'Northview Academy',
    'Demo District',
    'active',
    NOW(),
    NOW()
);

INSERT INTO users (
    id,
    organization_id,
    auth_user_id,
    email,
    full_name,
    role,
    status,
    created_at,
    updated_at
) VALUES (
    '33333333-3333-4333-8333-333333333333',
    '11111111-1111-4111-8111-111111111111',
    'auth-teacher-001',
    'teacher@northview.example',
    'Ava Johnson',
    'teacher',
    'active',
    NOW(),
    NOW()
);

INSERT INTO students (
    id,
    organization_id,
    school_id,
    student_number,
    first_name,
    last_name,
    grade_level,
    iep_status,
    birth_date,
    status,
    created_by,
    created_at,
    updated_at
) VALUES
(
    '44444444-4444-4444-8444-444444444444',
    '11111111-1111-4111-8111-111111111111',
    '22222222-2222-4222-8222-222222222222',
    'STU-1001',
    'Maya',
    'Patel',
    '5',
    TRUE,
    '2013-04-12',
    'active',
    '33333333-3333-4333-8333-333333333333',
    NOW(),
    NOW()
),
(
    '55555555-5555-4555-8555-555555555555',
    '11111111-1111-4111-8111-111111111111',
    '22222222-2222-4222-8222-222222222222',
    'STU-1002',
    'Leo',
    'Martinez',
    '4',
    FALSE,
    '2014-01-09',
    'active',
    '33333333-3333-4333-8333-333333333333',
    NOW(),
    NOW()
);