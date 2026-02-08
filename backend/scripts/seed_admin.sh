#!/bin/bash
set -e

# Load environment variables
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( dirname "$SCRIPT_DIR" )"

if [ -f "$BACKEND_DIR/.env" ]; then
    export $(cat "$BACKEND_DIR/.env" | grep -v '^#' | xargs)
else
    echo "❌ .env file not found."
    exit 1
fi

if [ -z "$MONGODB_URL" ]; then
    echo "❌ MONGODB_URL not found in .env"
    exit 1
fi

DB_NAME="${MONGODB_DB_NAME:-coresight}"

echo "========================================"
echo "  CoreSight Admin Seeder (Fixed)"
echo "========================================"
echo "📦 Database: $DB_NAME"

# 1. Create a temporary JavaScript file
# We use a known valid bcrypt hash for 'password123'
# The $ characters here are safe because we are writing to a file, not executing strictly yet.
cat > temp_seed_admin.js <<EOF
const dbName = '$DB_NAME';
const adminEmail = 'admin@gmail.com';
const realHash = '\$2b\$12\$K5yAbpp/xg1nH1wT9XLAUu.bbF1bc5lLCcoh7Kjop2oKa9t4keYtK';

// Connect to the specific DB
db = db.getSiblingDB(dbName);

const userDoc = {
    name: 'Admin User',
    email: adminEmail,
    password_hash: realHash,
    role: 'admin',
    hourly_rate: 0.0,
    skills: ['Administration', 'Management'],
    work_profile_embeddings: [],
    project_metrics: {},
    github_username: null,
    jira_account_id: null,
    created_at: new Date(),
    updated_at: new Date()
};

const existing = db.users.findOne({ email: adminEmail });

if (existing) {
    db.users.updateOne(
        { email: adminEmail },
        { \$set: { role: 'admin', password_hash: realHash, updated_at: new Date() } }
    );
    print('✅ UPDATE SUCCESS: Admin user updated.');
} else {
    db.users.insertOne(userDoc);
    print('✅ INSERT SUCCESS: New admin user created.');
}

// Verify count
print('Total users: ' + db.users.countDocuments());
EOF

# 2. Execute the file using mongosh
# We do NOT use --quiet so we can actually see errors if they happen
echo "🚀 Executing MongoDB script..."
mongosh "$MONGODB_URL" --file temp_seed_admin.js

# 3. Clean up
rm temp_seed_admin.js

echo ""
echo "========================================"
echo "  Done."
echo "========================================"