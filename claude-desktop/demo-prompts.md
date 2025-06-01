# Redis MCP Demo Script

This demo shows how developers can manage Redis databases and data through conversation instead of writing integration code. Instead of spending hours learning Redis commands and writing database scripts, developers can set up, test, and optimize Redis in minutes.

**Value for developers:**
- **Database setup**: Create and configure Redis databases instantly
- **Health monitoring**: Check database status without dashboards
- **Data seeding**: Populate test data through natural language
- **Query optimization**: Get Redis best practices automatically
- **Performance tuning**: AI suggests better data structures

Copy-paste these commands into Claude Desktop to run the demo:

## 1. Check Current Infrastructure

```
Show me my current Redis Cloud subscriptions and their status
```

*Shows existing databases and subscription details*

## 2. Database Health Check

```
Can you check the health and performance of my Redis databases?
```

*Displays connection status, memory usage, and performance metrics*

## 3. Create New Database

```
Create a new Redis database called "ecommerce-demo" using the Essentials free tier. Set it up for an e-commerce application with standard configuration.
```

*Creates database and provides connection details*

## 4. Seed Test Data - Products, Users, and Purchase Log

```
Create 5 products in the new database as hashes with keys product:1 through product:5. Include name, category, price, and stock_count fields. Use realistic e-commerce products like electronics and clothing.

Create 5 users as hashes with keys user:1 through user:5. Include name, email, join_date, and total_spent fields.

Create a purchase log with 10 transactions showing user purchases. Make some products more popular than others to simulate bestsellers. Store as purchase:1 through purchase:7 with user_id, product_id, quantity, and purchase_date.
```

*Creates realistic purchase data with popular items*

## 7. Query Current Setup

```
What are the top 3 most purchased products based on the purchase log? Show me the product details and total purchase count for each.
```

*Claude will iterate through purchases manually - shows current inefficiency*

## 8. Optimization Request

```
The query to find popular products seems slow and complex. How should I restructure the data to make finding the top products faster and easier? What Redis data structure would work best for product popularity rankings?
```

*AI suggests using sorted sets for rankings and explains why*

## 9. Implement Optimization

```
Create the optimized data structure you suggested and fill it in with the appopriate values
```

*Implements sorted set with purchase counts as scores*

## 10. Test Optimized Query

```
Now show me the top 3 most popular products using the optimized structure. Compare this to the previous method.
```

*Demonstrates instant results with ZREVRANGE vs manual iteration*


## Key Demo Points

- **No Redis expertise needed**: Developers describe what they want, AI handles implementation
- **Instant optimization advice**: AI suggests Redis best practices automatically  
- **Production patterns**: Shows real database optimization scenarios
- **Time savings**: Database setup and testing in minutes, not hours
- **Learning built-in**: Developers learn Redis patterns through natural language explanations
