-- seed_aws_architecture_db.sql

-- Create the table for storing system prompts
CREATE TABLE IF NOT EXISTS system_prompts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt_name TEXT UNIQUE NOT NULL,
    prompt_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the table for storing versioned responses
CREATE TABLE IF NOT EXISTS versioned_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    architecture_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_text TEXT NOT NULL,
    front_content TEXT NOT NULL,
    back_content TEXT NOT NULL,
    system_prompt_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (system_prompt_id) REFERENCES system_prompts(id)
);

-- Insert system prompts
INSERT OR IGNORE INTO system_prompts (prompt_name, prompt_text) VALUES 
('default_aws_architect', 'You are an AWS architect. Provide clear and concise explanations of AWS reference architectures.'),
('security_focused', 'Focus on the security aspects of AWS architectures. Highlight best practices and potential vulnerabilities.'),
('cost_optimization', 'Analyze the AWS architecture with a focus on cost optimization. Suggest potential areas for reducing expenses.'),
('performance_tuning', 'Examine the AWS architecture for performance bottlenecks and suggest optimizations.');

-- Insert mocked versioned responses
INSERT INTO versioned_responses (architecture_name, provider, model, user_text, front_content, back_content, system_prompt_id)
VALUES 
-- Electric Vehicle Charging responses
('electric-vehicle-charging-ocpp-handler', 'ollama', 'llama2', 'Describe the EV charging architecture', 'Front: AWS-based EV charging system using OCPP', 'Back: Utilizes API Gateway, Lambda, DynamoDB for real-time charging management', 1),
('electric-vehicle-charging-ocpp-handler', 'ollama', 'mistral', 'Explain OCPP in EV charging', 'Front: Open Charge Point Protocol in AWS', 'Back: Standardized communication between charging stations and management systems', 1),
('electric-vehicle-charging-ocpp-handler', 'openai', 'gpt-3.5-turbo', 'EV charging security considerations', 'Front: Security in AWS EV charging solutions', 'Back: Encryption, IAM roles, VPC design for secure charging networks', 2),
('electric-vehicle-charging-ocpp-handler', 'anthropic', 'claude-2', 'Cost optimization for EV charging', 'Front: Optimizing costs in AWS EV charging architecture', 'Back: Using AWS Auto Scaling, Reserved Instances, and S3 Intelligent-Tiering', 3),

-- Serverless Data Lake responses
('serverless-data-lake-foundation', 'ollama', 'llama2', 'Explain serverless data lake', 'Front: AWS Serverless Data Lake Architecture', 'Back: Uses S3, Athena, Glue, and Lambda for scalable data processing', 1),
('serverless-data-lake-foundation', 'openai', 'gpt-4', 'Data lake security best practices', 'Front: Securing AWS Serverless Data Lake', 'Back: Implement S3 bucket policies, KMS encryption, and Lake Formation', 2),
('serverless-data-lake-foundation', 'anthropic', 'claude-2', 'Optimize data lake costs', 'Front: Cost-effective AWS Data Lake', 'Back: Utilize S3 lifecycle policies, Glue job bookmarks, and Athena query optimization', 3),

-- Containerized Microservices responses
('containerized-microservices', 'ollama', 'mistral', 'Describe containerized microservices', 'Front: AWS Containerized Microservices Architecture', 'Back: ECS/EKS, App Mesh, CloudMap for service discovery', 1),
('containerized-microservices', 'openai', 'gpt-3.5-turbo', 'Microservices security', 'Front: Securing Containerized Microservices on AWS', 'Back: IAM roles for tasks, network policies, secrets management with AWS Secrets Manager', 2),
('containerized-microservices', 'anthropic', 'claude-2', 'Performance tuning for microservices', 'Front: Optimizing AWS Microservices Performance', 'Back: Use of Application Load Balancer, X-Ray for tracing, CloudWatch for monitoring', 4);

-- Example query to verify data
SELECT vr.architecture_name, vr.provider, vr.model, vr.user_text, sp.prompt_name
FROM versioned_responses vr
JOIN system_prompts sp ON vr.system_prompt_id = sp.id
ORDER BY vr.architecture_name, vr.created_at;
