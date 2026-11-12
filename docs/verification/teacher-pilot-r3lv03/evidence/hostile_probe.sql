-- Independent hostile probe of migration 006 (PR #35 head 7a72792).
-- Synthetic data only. Runs in a scratch database created for this probe.
\set ON_ERROR_STOP off
\pset tuples_only on
\pset format unaligned

-- Seed as superuser (bypasses RLS) -----------------------------------------
INSERT INTO organizations (id,name,type) VALUES
 ('a0000000-0000-0000-0000-00000000000a','Synthetic Org A','pilot'),
 ('b0000000-0000-0000-0000-00000000000b','Synthetic Org B','pilot');
INSERT INTO users (id,organization_id,auth_user_id,email,full_name,role) VALUES
 ('a1000000-0000-0000-0000-000000000001','a0000000-0000-0000-0000-00000000000a','aaaaaaaa-0000-4000-8000-00000000000a','a@t.invalid','A Teacher','teacher'),
 ('a2000000-0000-0000-0000-000000000002','a0000000-0000-0000-0000-00000000000a','aaaaaaaa-0000-4000-8000-0000000000ff','ar@t.invalid','A Revoked','teacher'),
 ('b1000000-0000-0000-0000-000000000001','b0000000-0000-0000-0000-00000000000b','bbbbbbbb-0000-4000-8000-00000000000b','b@t.invalid','B Teacher','teacher');
INSERT INTO students (id,organization_id,first_name,last_name,created_by) VALUES
 ('a3000000-0000-0000-0000-000000000003','a0000000-0000-0000-0000-00000000000a','Synth','Student','a1000000-0000-0000-0000-000000000001');
INSERT INTO assessments (id,organization_id,student_id,created_by,title,assessment_type) VALUES
 ('a4000000-0000-0000-0000-000000000004','a0000000-0000-0000-0000-00000000000a','a3000000-0000-0000-0000-000000000003','a1000000-0000-0000-0000-000000000001','Synthetic CER','ela');
INSERT INTO ai_feedback_requests (id,organization_id,assessment_id,student_id,created_by,request_key,input_sha256,data_classification,response_text,rubric_id,rubric_version,rubric_sha256,prompt_version,provider,model_id,reserved_cost_microusd) VALUES
 ('a5000000-0000-0000-0000-000000000005','a0000000-0000-0000-0000-00000000000a','a4000000-0000-0000-0000-000000000004','a3000000-0000-0000-0000-000000000003','a1000000-0000-0000-0000-000000000001','c0000000-0000-0000-0000-000000000001',repeat('a',64),'synthetic','SECRET-STUDENT-TEXT-MARKER','RUB','v1',repeat('b',64),'p1','anthropic','m',10);
INSERT INTO ai_feedback_drafts (id,organization_id,request_id,status,output,draft_text) VALUES
 ('a6000000-0000-0000-0000-000000000006','a0000000-0000-0000-0000-00000000000a','a5000000-0000-0000-0000-000000000005','ready','{}'::jsonb,'Draft text');
INSERT INTO ai_feedback_decisions (id,organization_id,draft_id,decided_by,decision,approved_text,teacher_confirmed,decision_key,payload_sha256) VALUES
 ('a7000000-0000-0000-0000-000000000007','a0000000-0000-0000-0000-00000000000a','a6000000-0000-0000-0000-000000000006','a1000000-0000-0000-0000-000000000001','accepted','Draft text',true,'d0000000-0000-0000-0000-000000000001',repeat('c',64));

-- P1 audit correlation: decision row has an audit row with the same id and actor, no student text
SELECT 'P1_audit_decision_rows=' || count(*) FROM audit_logs
 WHERE entity_id='a7000000-0000-0000-0000-000000000007' AND performed_by='a1000000-0000-0000-0000-000000000001';
SELECT 'P1_audit_draft_rows=' || count(*) FROM audit_logs WHERE entity_id='a6000000-0000-0000-0000-000000000006';
SELECT 'P1_audit_leaks_student_text=' || count(*) FROM audit_logs WHERE metadata::text LIKE '%SECRET-STUDENT-TEXT-MARKER%';

-- Cross-tenant attacker: Org B teacher -----------------------------------
SET ROLE authenticated;
SELECT set_config('request.jwt.claims','{"sub":"bbbbbbbb-0000-4000-8000-00000000000b","role":"authenticated"}',false);
SELECT 'P2_B_sees_A_requests=' || count(*) FROM ai_feedback_requests;
SELECT 'P2_B_sees_A_drafts=' || count(*) FROM ai_feedback_drafts;
SELECT 'P2_B_sees_A_decisions=' || count(*) FROM ai_feedback_decisions;
SELECT 'P2_B_sees_A_audit=' || count(*) FROM audit_logs;
SELECT 'P2_B_by_id=' || count(*) FROM ai_feedback_drafts WHERE id='a6000000-0000-0000-0000-000000000006';
\echo P3_B_insert_decision_on_A_draft:
INSERT INTO ai_feedback_decisions (id,organization_id,draft_id,decided_by,decision,approved_text,teacher_confirmed,decision_key,payload_sha256)
 VALUES (gen_random_uuid(),'a0000000-0000-0000-0000-00000000000a','a6000000-0000-0000-0000-000000000006','b1000000-0000-0000-0000-000000000001','revised','pwned',true,gen_random_uuid(),repeat('d',64));
\echo P4_B_call_reserve_function:
SELECT public.aeos_reserve_ai_feedback_request('{}'::jsonb,'{}'::jsonb);

-- Same-tenant teacher: append-only must hold even for the owner ----------
SELECT set_config('request.jwt.claims','{"sub":"aaaaaaaa-0000-4000-8000-00000000000a","role":"authenticated"}',false);
SELECT 'P5_A_sees_own_decisions=' || count(*) FROM ai_feedback_decisions;
\echo P6_A_update_own_decision_no_where:
UPDATE ai_feedback_decisions SET approved_text='tampered';
\echo P7_A_delete_own_decision:
DELETE FROM ai_feedback_decisions WHERE id='a7000000-0000-0000-0000-000000000007';
\echo P8_A_direct_insert_decision:
INSERT INTO ai_feedback_decisions (id,organization_id,draft_id,decided_by,decision,approved_text,teacher_confirmed,decision_key,payload_sha256)
 VALUES (gen_random_uuid(),'a0000000-0000-0000-0000-00000000000a','a6000000-0000-0000-0000-000000000006','a1000000-0000-0000-0000-000000000001','revised','direct',true,gen_random_uuid(),repeat('e',64));
\echo P9_A_delete_audit:
DELETE FROM audit_logs;
RESET ROLE;
SELECT 'P10_decision_text_after_attacks=' || approved_text FROM ai_feedback_decisions WHERE id='a7000000-0000-0000-0000-000000000007';
SELECT 'P10_decision_count_after_attacks=' || count(*) FROM ai_feedback_decisions;
SELECT 'P10_audit_count_after_attacks=' || count(*) FROM audit_logs;

-- Revoked access: disable then suspend ----------------------------------
UPDATE users SET status='disabled' WHERE id='a1000000-0000-0000-0000-000000000001';
SET ROLE authenticated;
SELECT set_config('request.jwt.claims','{"sub":"aaaaaaaa-0000-4000-8000-00000000000a","role":"authenticated"}',false);
SELECT 'P11_disabled_member_sees_drafts=' || count(*) FROM ai_feedback_drafts;
RESET ROLE;
UPDATE users SET status='active' WHERE id='a1000000-0000-0000-0000-000000000001';
UPDATE organizations SET status='suspended' WHERE id='a0000000-0000-0000-0000-00000000000a';
SET ROLE authenticated;
SELECT set_config('request.jwt.claims','{"sub":"aaaaaaaa-0000-4000-8000-00000000000a","role":"authenticated"}',false);
SELECT 'P12_suspended_org_sees_drafts=' || count(*) FROM ai_feedback_drafts;
SELECT set_config('request.jwt.claims','{"role":"anon"}',false);
RESET ROLE;
SET ROLE anon;
SELECT 'P13_anon_sees_drafts=' || count(*) FROM ai_feedback_drafts;
RESET ROLE;
