-- ===============================================================================
-- FILE: backend/migrations/001_enable_rls.sql
-- PURPOSE: Enable Row-Level Security on PostgreSQL Database
-- ARCHITECTURE: Database Migration
-- INPUTS: None
-- OUTPUTS: Secured database tables
-- HACKATHON VERTICAL: Security & Privacy
-- ===============================================================================

-- Ensure RLS is enabled for the tickets table
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;

-- Fans can only see their own tickets
CREATE POLICY fan_read_own_tickets ON tickets
FOR SELECT
USING (id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Admins see all tickets
CREATE POLICY admin_read_all_tickets ON tickets
FOR SELECT
USING (current_setting('request.jwt.claims', true)::json->>'role' = 'admin');

-- Ensure RLS is enabled for the incidents table
ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;

-- Fans can read incidents they reported
CREATE POLICY fan_read_own_incidents ON incidents
FOR SELECT
USING (reporter_id = current_setting('request.jwt.claims', true)::json->>'sub');

-- Admins see all incidents
CREATE POLICY admin_read_all_incidents ON incidents
FOR SELECT
USING (current_setting('request.jwt.claims', true)::json->>'role' = 'admin');

-- Ensure RLS is enabled for the audit_logs table
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Only admins can read audit logs
CREATE POLICY admin_read_all_audit_logs ON audit_logs
FOR SELECT
USING (current_setting('request.jwt.claims', true)::json->>'role' = 'admin');
