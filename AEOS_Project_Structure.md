# AEOS Project Structure

## Overview
AEOS is being reframed as the AEOS Intervention Intelligence Platform, a focused SaaS product for teachers and special education teams to identify student needs, generate intervention recommendations, and track support actions with AI assistance.

## Product Positioning
The initial product should not attempt to be a full education operating system. The MVP is a secure, pragmatic workflow tool for:
- Teacher-led case review
- SPED and intervention planning
- Assessment intake and interpretation
- AI-assisted recommendation drafting
- Audit-friendly recordkeeping

## Design Principles
- Prioritize teacher and SPED workflow over broad platform ambition
- Keep the MVP narrow, reliable, and easy to pilot
- Protect sensitive student data with strong access controls
- Make AI assistance helpful but bounded and reviewable
- Build for pilot schools first, then expand

## MVP Goals
- Support secure teacher workflows for student support planning
- Capture student context, assessments, and intervention activity
- Generate structured AI recommendations that can be reviewed and edited
- Provide audit trails for compliance and trust
- Enable pilot evaluation with minimal complexity

## MVP Architecture

### 1. Frontend
Framework: Next.js + React

Purpose: teacher-facing workspace for intervention planning.

Core modules:
- Authentication and onboarding
- Student overview dashboard
- Assessment intake and review
- Intervention plan workspace
- Recommendation history and notes
- Basic reporting and export

### 2. Backend
Framework: FastAPI

Purpose: orchestrate business logic, secure data access, and AI outputs.

Core services:
- Authentication and session service
- User and role management service
- School and tenant context service
- Student profile service
- Assessment service
- Intervention planning service
- AI recommendation service
- Audit logging service

### 3. Database
Platform: Supabase PostgreSQL

Purpose: persistent storage for students, workflows, and review history.

Core entities:
- tenants
- users
- roles
- schools
- students
- assessments
- assessment_results
- intervention_plans
- intervention_actions
- notes
- audit_logs
- ai_recommendation_runs

### 4. Security Model
The system must be designed as a secure multi-tenant SaaS from day one.

Key requirements:
- Authentication via Supabase Auth or equivalent provider
- Role-based access control for teacher, case manager, admin, and support roles
- Tenant scoping so data is isolated by school or district context
- Least-privilege access to student records
- Encrypted storage for sensitive files and content
- Audit logging for all create, update, delete, and export actions
- Secret management for API keys and model access

### 5. AI Safety Controls
AI should assist, not replace human judgment.

Required controls:
- Prompt templates with bounded scope
- Human review before final use in sensitive workflows
- Output validation and structured response formats
- Logging of model inputs/outputs for traceability
- Clear disclaimers for AI-generated recommendations
- No autonomous actions without explicit review

### 6. Deployment Approach
- Frontend: Vercel
- Backend: Render, Railway, or Fly.io
- Database: Supabase PostgreSQL
- File storage: Supabase Storage
- Monitoring: Sentry, basic logging, and error tracking
- CI/CD: separate staging and production environments

## Suggested Repository Structure
```text
AEOS/
  README.md
  docs/
    architecture/
    product/
    research/
    pilots/
  backend/
    app/
    tests/
  frontend/
    app/
    components/
    lib/
  database/
```

## MVP Database Entity Model

### tenants
- id
- name
- type
- created_at

### users
- id
- tenant_id
- auth_user_id
- email
- full_name
- role
- created_at

### schools
- id
- tenant_id
- name
- district_name
- created_at

### students
- id
- tenant_id
- school_id
- first_name
- last_name
- grade_level
- iep_status
- created_at

### assessments
- id
- tenant_id
- student_id
- created_by
- assessment_type
- status
- created_at

### assessment_results
- id
- assessment_id
- score
- performance_band
- notes
- created_at

### intervention_plans
- id
- tenant_id
- student_id
- created_by
- title
- status
- summary
- created_at

### intervention_actions
- id
- intervention_plan_id
- action_type
- description
- assigned_to
- due_date
- status
- created_at

### notes
- id
- tenant_id
- student_id
- author_id
- content
- created_at

### audit_logs
- id
- tenant_id
- entity_type
- entity_id
- action
- performed_by
- created_at

### ai_recommendation_runs
- id
- tenant_id
- student_id
- request_context
- model_response
- created_by
- created_at

## API Structure
The API should stay simple and feature-focused.

### Core API Areas
- Auth
  - POST /auth/login
  - POST /auth/logout
  - GET /auth/me
- Users and roles
  - GET /users
  - POST /users
  - PATCH /users/{id}
- Students
  - GET /students
  - POST /students
  - GET /students/{id}
  - PATCH /students/{id}
- Assessments
  - GET /assessments
  - POST /assessments
  - GET /assessments/{id}
- Intervention plans
  - GET /intervention-plans
  - POST /intervention-plans
  - PATCH /intervention-plans/{id}
- AI recommendations
  - POST /recommendations/generate
  - GET /recommendations/{id}
- Audit logs
  - GET /audit-logs

## Frontend Modules
- Sign-in and role-based landing page
- Student directory and profile view
- Assessment intake workflow
- Intervention plan workspace
- Recommendation review and editing panel
- Basic reporting and export views

## MVP Scope
The MVP should include:
- Authentication and role-based access
- Multi-tenant foundation
- Student profile management
- Assessment intake and results viewing
- Intervention plan creation
- AI-generated recommendation drafts
- Audit logging
- Basic dashboard and reporting

## Pilot Version
The pilot version can expand slightly to support:
- Limited onboarding and support flows
- Enhanced reporting for school leadership
- Better note-taking and collaboration
- Optional file attachments for evidence

## Scale Version
The scale version can include:
- District-level reporting and rollups
- Advanced workflow automation
- Deeper integrations with SIS/LMS systems
- Expanded AI reasoning and personalization
- Parent and caregiver communication features
- Broader analytics and forecasting

## Non-Functional Requirements
- Secure authentication
- Tenant-aware authorization
- Auditability of all sensitive actions
- Low-latency API responses for teacher workflows
- Clear data retention and deletion handling
- Scalable architecture for pilot growth
