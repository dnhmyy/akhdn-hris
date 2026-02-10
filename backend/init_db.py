# Update SQL statements to include device_id and device_branch columns in the attendance table.

ALTER TABLE attendance
ADD COLUMN device_id VARCHAR(255),  -- Add device_id column
ADD COLUMN device_branch VARCHAR(255);  -- Add device_branch column

-- Ensure any necessary data migration scripts are added to handle existing records.