-- 1) Show ten rows from the incidents table
SELECT * FROM incidents LIMIT 10;

-- 2) Which service has the most incident records?
SELECT service, COUNT(*) AS incident_count
FROM incidents
GROUP BY service
ORDER BY incident_count DESC;

-- 3) Show high-priority (P1 and P2) incidents
SELECT incident_id, service, priority, affected_users
FROM incidents
WHERE priority IN ('P1', 'P2')
ORDER BY affected_users DESC;

-- 4) Look only at Payroll (the three sample incident records)
SELECT incident_id, opened_at, status, affected_users, priority_score
FROM incidents
WHERE service = 'Payroll & HR Portal'
ORDER BY opened_at;

-- 5) Match an incident date to a daily measurement using a basic JOIN
SELECT i.incident_id, i.service, d.date, d.error_rate_pct
FROM incidents i
JOIN service_daily d ON i.service = d.service
    AND substr(i.opened_at, 1, 10) = d.date;
