# Railway.app Deployment Guide

## What You'll Get

After following this guide, you'll have:
- ✅ A live website (e.g., `https://your-app.up.railway.app`)
- ✅ Secure login with username/password
- ✅ PostgreSQL database (hosted by Railway)
- ✅ HTTPS encryption (automatic)
- ✅ Automatic updates when you push to GitHub
- ✅ Access from anywhere (computer, phone, tablet)

**Total time: 10-15 minutes**

---

## Step 1: Push Your Code to GitHub

First, make sure all your latest code is on GitHub:

```bash
cd ~/Documents/GitHub/finance
git pull  # Get latest changes
git status  # Should show "nothing to commit, working tree clean"
```

If you see uncommitted changes:
```bash
git add .
git commit -m "Ready for Railway deployment"
git push
```

---

## Step 2: Create Railway Account

1. Visit: **https://railway.app**
2. Click **"Login"** (top right)
3. Choose **"Login with GitHub"**
4. Authorize Railway to access your GitHub

**That's it!** No credit card required for the free tier.

---

## Step 3: Deploy Your App

### 3.1 Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository: **`tonywallace1978-collab/finance`**
4. Select branch: **`claude/fix-btc-price-tracking-011CUYEtWBBdWYnTSp2jMrPB`**

Railway will automatically detect it's a Python/Flask app and start building.

### 3.2 Add PostgreSQL Database

1. In your project, click **"+ New"**
2. Select **"Database"**
3. Choose **"Add PostgreSQL"**

Railway will automatically:
- Create the database
- Set the `DATABASE_URL` environment variable
- Connect it to your app

### 3.3 Set Environment Variables

1. Click on your **app service** (not the database)
2. Go to **"Variables"** tab
3. Click **"+ New Variable"**
4. Add these variables:

| Variable | Value |
|----------|-------|
| `SECRET_KEY` | Generate one below ⬇️ |
| `FLASK_ENV` | `production` |

**To generate SECRET_KEY:**

Open a terminal and run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output (it will look like: `a1b2c3d4e5...`) and paste it as the `SECRET_KEY` value.

### 3.4 Deploy

Railway automatically deploys your app. Wait for the build to complete (1-2 minutes).

You'll see:
- ✅ Build logs
- ✅ "Success" message
- ✅ Your app URL

---

## Step 4: Get Your App URL

1. Click on your app service
2. Go to **"Settings"** tab
3. Scroll to **"Domains"**
4. Click **"Generate Domain"**

Railway will give you a URL like:
```
https://finance-production-xxxx.up.railway.app
```

**This is your app!** Anyone with this URL can visit it (but they need login credentials).

---

## Step 5: Create Your User Account

Now you need to create your login credentials.

### 5.1 Open Railway CLI

Railway provides a web-based terminal. In your project:

1. Click on your **app service**
2. Go to **"Deployments"** tab
3. Click on the latest deployment
4. Click **"View Logs"**
5. Look for **"Deploy"** or **"Connect"** button/option

Alternatively, you can SSH in:

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login:
   ```bash
   railway login
   ```

3. Link to your project:
   ```bash
   railway link
   ```

4. Run the create user script:
   ```bash
   railway run python create_user.py
   ```

### 5.2 Create User

When prompted:
```
Enter username: tony
Enter password: (type a strong password - at least 8 characters)
Confirm password: (type it again)
Enter email (optional): (can leave blank)
```

You'll see:
```
✓ User 'tony' created successfully!
```

---

## Step 6: Login to Your App!

1. Visit your Railway URL
2. You'll see the login page
3. Enter your username and password
4. Click **"Login"**

**You're in!** 🎉

You should see your complete financial dashboard.

---

## Step 7: Import Your Data

Your app is running, but it doesn't have your financial data yet.

### Option A: Manual Entry

1. Go to **"Manual Entries"**
2. Click **"Edit"** on each entry
3. Update with your actual values:
   - Tony 401K: $314,000
   - Heather 401K: $75,000
   - Cash: $492,000
   - etc.

### Option B: Import Database (Advanced)

If you have a local database with all your assets:

1. Export your local database to SQL:
   ```bash
   # On your computer
   sqlite3 instance/finance.db .dump > dump.sql
   ```

2. Convert to PostgreSQL format (Railway provides tools for this)

3. Import via Railway CLI

(This is more advanced - start with Manual Entry if unsure)

---

## Step 8: Update Prices

Click **"Update Prices"** button on the dashboard to fetch current prices for all assets.

This will take 2-3 minutes the first time (fetching 77+ assets).

---

## Automatic Updates

Now that you're deployed, Railway automatically updates your app when you push to GitHub:

```bash
# Make changes locally
git add .
git commit -m "Update something"
git push
```

Railway will:
1. Detect the push
2. Rebuild your app
3. Deploy automatically
4. Your URL stays the same

**No manual deployment needed!**

---

## Custom Domain (Optional)

Want to use your own domain instead of `*.up.railway.app`?

1. Go to **"Settings"** → **"Domains"**
2. Click **"Custom Domain"**
3. Enter your domain (e.g., `finances.yourdomain.com`)
4. Follow DNS instructions

Railway provides free HTTPS certificates for custom domains.

---

## Security Notes

### Your Data is Secure

- ✅ **HTTPS encryption** - All traffic is encrypted
- ✅ **Password hashing** - Passwords are never stored in plain text
- ✅ **Session security** - Uses secure Flask sessions
- ✅ **Environment variables** - Secrets stored securely, not in code

### What Can Someone Do If They Get Your URL?

- ❌ **Cannot** access without login
- ❌ **Cannot** see your data without credentials
- ❌ **Cannot** trade or transfer your assets

Even if someone got your URL, they'd see the login page and that's it.

### Sharing Access

To let someone else access (like your wife):

```bash
# On your computer or via Railway CLI
railway run python create_user.py
```

Create a separate account for them with a different username.

---

## Monitoring & Logs

### View Logs

In Railway:
1. Click your app service
2. Go to **"Deployments"**
3. Click latest deployment
4. See real-time logs

### Check Usage

Railway free tier includes:
- $5 of usage per month
- Usually enough for a small personal app
- Check usage in **"Usage"** tab

If you exceed free tier, Railway will notify you before charging.

---

## Troubleshooting

### App Won't Start

Check the logs for errors:
1. Go to **"Deployments"**
2. Click the failed deployment
3. Look for error messages in logs

Common issues:
- Missing `SECRET_KEY` environment variable
- Database connection issues
- Syntax errors in code

### Can't Login

Make sure you created a user account:
```bash
railway run python create_user.py
```

### Database Errors

Railway automatically connects PostgreSQL. If you see database errors:
1. Make sure PostgreSQL service is running
2. Check that `DATABASE_URL` is set in environment variables
3. Try redeploying

### Prices Not Updating

The price fetcher may hit API rate limits. Try:
1. Wait a few minutes
2. Click "Update Prices" again
3. Check logs for specific errors

---

## Cost

### Railway Free Tier

- **$5 credit per month** (usage-based)
- Typical usage for this app: **~$2-3/month**
- **No credit card required** to start

### If You Need More

- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage

For a personal finance tracker, **free tier should be sufficient**.

---

## What's Next?

Now that your app is deployed:

1. **Add all your assets** (if not already imported)
2. **Update manual entries** (401K, cash, etc.)
3. **Add business metrics** (contractors, revenue)
4. **Bookmark your URL**
5. **Set up price update reminder** (click "Update Prices" weekly)

### Mobile Access

Your Railway URL works on mobile!
- Open in browser
- Login with same credentials
- Bookmark for easy access
- Works on iPhone, Android, tablets

---

## Need Help?

If you get stuck:
1. Check Railway logs for errors
2. Verify all environment variables are set
3. Make sure PostgreSQL is connected
4. Try redeploying

Common questions:
- **How do I add more users?** Run `railway run python create_user.py`
- **How do I change my password?** Run the create_user script again (will update existing user)
- **Can I use a custom domain?** Yes! See "Custom Domain" section above
- **Is my data backed up?** Railway backs up PostgreSQL databases automatically

---

## Success Checklist

✅ Pushed code to GitHub
✅ Created Railway account
✅ Deployed app from GitHub
✅ Added PostgreSQL database
✅ Set SECRET_KEY environment variable
✅ Generated Railway domain
✅ Created user account
✅ Logged in successfully
✅ See dashboard with financial data

**If you checked all these, you're done!** 🎉

Visit your URL from anywhere and enjoy your personal financial tracker!
