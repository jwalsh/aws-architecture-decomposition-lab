-- Create the table for storing versioned responses
CREATE TABLE versioned_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    architecture_name TEXT NOT NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    user_text TEXT NOT NULL,
    front_content TEXT NOT NULL,
    back_content TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert example data
INSERT INTO versioned_responses (architecture_name, provider, model, user_text, front_content, back_content, system_prompt)
VALUES 
('electric-vehicle-charging-ocpp-handler', 'ollama', 'llama2', 'Describe the EV charging architecture', 'Front content for EV charging...', 'Back content for EV charging...', 'You are an AWS architect...'),
('electric-vehicle-charging-ocpp-handler', 'ollama', 'mistral', 'Explain OCPP in EV charging', 'OCPP front content...', 'OCPP back content...', 'Explain AWS architectures...'),
('electric-vehicle-charging-ocpp-handler', 'ollama', 'llama2', 'EV charging security considerations', 'Security front content...', 'Security back content...', 'Focus on AWS security...');

-- Example query to get all responses for 'electric-vehicle-charging-ocpp-handler' using ollama
SELECT model, user_text, front_content, back_content, created_at
FROM versioned_responses
WHERE architecture_name = 'electric-vehicle-charging-ocpp-handler' AND provider = 'ollama'
ORDER BY created_at DESC;
