set -e

echo "Resetting kiosk interaction data..."

set -a
source .env
set +a

psql "host=$DB_HOST port=$DB_PORT dbname=$DB_NAME user=$DB_USER sslmode=require" <<SQL
TRUNCATE TABLE kiosk_interaction RESTART IDENTITY;
SQL

echo "kiosk_interaction table has been reset successfully."