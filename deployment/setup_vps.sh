#!/bin/bash

# تحديث النظام
echo "Updating system..."
sudo apt-get update
sudo apt-get upgrade -y

# تثبيت الحزم الضرورية
echo "Installing dependencies..."
sudo apt-get install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx curl

# تثبيت Virtualenv
sudo pip3 install virtualenv

# إعداد قاعدة البيانات
echo "Setting up PostgreSQL..."
# ملاحظة: يجب تعديل كلمة المرور واسم المستخدم أدناه
# sudo -u postgres psql -c "CREATE DATABASE inventory_db;"
# sudo -u postgres psql -c "CREATE USER inventory_user WITH PASSWORD 'strong_db_password';"
# sudo -u postgres psql -c "ALTER ROLE inventory_user SET client_encoding TO 'utf8';"
# sudo -u postgres psql -c "ALTER ROLE inventory_user SET default_transaction_isolation TO 'read committed';"
# sudo -u postgres psql -c "ALTER ROLE inventory_user SET timezone TO 'UTC';"
# sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;"

echo "Setup script completed. Please follow the manual steps in README_DEPLOY.md for configuration."
