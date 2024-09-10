-- Drop tables if they exist (for demo/re-seeding)
DROP TABLE IF EXISTS frequencies;
DROP TABLE IF EXISTS services;

-- Create Services Table
CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    icon_url TEXT
);

-- Create Frequencies Table (Source/Sink Counter)
CREATE TABLE frequencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_service TEXT NOT NULL,
    sink_service TEXT NOT NULL,
    count INTEGER DEFAULT 1,
    FOREIGN KEY (source_service) REFERENCES services (name),
    FOREIGN KEY (sink_service) REFERENCES services (name),
    UNIQUE (source_service, sink_service)
);

-- Insert Sample Service Data (from aws_icons_mapping)
INSERT INTO services (name, icon_url)
VALUES
    ('amplify', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_AWS-Amplify_48.png'),
    ('apigateway', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_Amazon-API-Gateway_48.png'),
    ('appflow', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_Amazon-AppFlow_48.png'),
    ('appstream', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_Amazon-AppStream-2_48.png'),
    ('athena', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_Amazon-Athena_48.png'),
    ('aurora', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_Amazon-Aurora_48.png'),
    ('backup', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_AWS-Backup_48.png'),
    ('batch', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_AWS-Batch_48.png'),
    -- ... (Insert ALL other services from aws_icons_mapping here)
    ('xray', 'https://wal.sh/static/images/aws-architecture-diagrams-assets/Arch_AWS-X-Ray_48.png');

-- Insert Sample Frequency Data (Mock Data)
INSERT INTO frequencies (source_service, sink_service, count)
VALUES
    ('apigateway', 'lambda', 120),
    ('lambda', 'dynamodb', 85),
    ('lambda', 's3', 35),
    ('cloudfront', 's3', 500),
    ('route53', 'cloudfront', 1000),
    ('cognito', 'lambda', 75);
    
-- Example Query with Mock Data (Top 5 Frequent Interactions)
SELECT
    f.source_service,
    ss.icon_url AS source_icon,
    f.sink_service,
    sk.icon_url AS sink_icon,
    f.count
FROM frequencies f
JOIN services ss ON f.source_service = ss.name
JOIN services sk ON f.sink_service = sk.name
ORDER BY f.count DESC
LIMIT 5;
