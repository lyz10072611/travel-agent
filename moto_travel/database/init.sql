-- 摩旅智能助手数据库初始化脚本

-- 创建pgvector扩展
CREATE EXTENSION IF NOT EXISTS vector;

-- 创建数据库用户（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'moto_travel') THEN
        CREATE USER moto_travel WITH PASSWORD 'password';
    END IF;
END
$$;

-- 授予权限
GRANT ALL PRIVILEGES ON DATABASE moto_travel TO moto_travel;
GRANT ALL PRIVILEGES ON SCHEMA public TO moto_travel;

-- 创建索引模板函数
CREATE OR REPLACE FUNCTION create_vector_index(table_name text, column_name text, index_name text)
RETURNS void AS $$
BEGIN
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I ON %I USING ivfflat (%I vector_cosine_ops) WITH (lists = 100)', 
                   index_name, table_name, column_name);
END;
$$ LANGUAGE plpgsql;
