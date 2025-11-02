-- 创建任务状态的枚举类型
CREATE TYPE plan_task_status AS ENUM ('queued', 'in_progress', 'success', 'error');

-- 创建plan_tasks表
CREATE TABLE IF NOT EXISTS plan_tasks (
    id SERIAL PRIMARY KEY,
    trip_plan_id VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    status plan_task_status NOT NULL,
    input_data JSONB NOT NULL,
    output_data JSONB,
    error_message VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 在trip_plan_id上创建索引以加快查找
CREATE INDEX IF NOT EXISTS idx_plan_tasks_trip_plan_id ON plan_tasks(trip_plan_id);

-- 在status上创建索引以加快过滤
CREATE INDEX IF NOT EXISTS idx_plan_tasks_status ON plan_tasks(status);

-- 创建触发器以自动更新updated_at时间戳
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_plan_tasks_updated_at
    BEFORE UPDATE ON plan_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();