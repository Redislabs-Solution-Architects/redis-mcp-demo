# Redis MCP Demo Commands

**Skip the Redis learning curve.** Manage databases through chat instead of code. What normally takes hours, now takes minutes

Copy-paste these into Claude Desktop:

## 1. Check Current Infrastructure
```
Show me my current Redis Cloud subscriptions and their status
```

## 2. Database Health Check

```
Can you check the health and performance of my Redis databases?
```

## 3. Create New Database

```
Create a new Redis database called "ecommerce-demo" using the Essentials free tier. Set it up for an e-commerce application with standard configuration.
```

*Creates database and provides connection details*

## 4. Seed Test Data - Products, Users, and Purchase Log

**IMPORTANT: You can only do Database Operations on the Database defined in your config. It will not do it on the database most recently created.**

```
Create 3 products as hashes with keys product:1 through product:3. Include name and price fields.

Create 3 users as hashes with keys user:1 through user:3. Include name and email.

Create a purchase log with 5 transactions showing user purchases. Make some products more popular than others to simulate bestsellers. Store as purchase:1 through purchase:7 with user_id and product_id.
```

## 7. Query Current Setup

```
What are the top 3 most purchased products based on the purchase log? Show me the product details and total purchase count for each.
```

*Claude will iterate through purchases manually - shows current inefficiency*

## 8. Optimization Request

```
The query to find popular products seems slow and complex. How should I restructure the data to make finding the top products faster and easier? What Redis data structure would work best for product popularity rankings? Implement it and fill in data.
```

*LLM suggests using sorted sets for rankings and explains why and implements it*

## 9. Test Optimized Query

```
Now show me the top 3 most popular products using the optimized structure. Compare this to the previous method.
```

*Demonstrates instant results with ZREVRANGE vs manual iteration*
