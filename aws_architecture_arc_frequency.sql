-- Query to Get Top N Most Frequent Arcs with Service Names and Icons
SELECT 
    ss.name AS source_service, 
    ss.icon_url AS source_icon,
    sk.name AS sink_service,
    sk.icon_url AS sink_icon,
    f.count AS interaction_count
FROM frequencies f
JOIN services ss ON f.source_service = ss.name
JOIN services sk ON f.sink_service = sk.name
ORDER BY f.count DESC
LIMIT 10; -- Adjust this limit to get your desired top N
