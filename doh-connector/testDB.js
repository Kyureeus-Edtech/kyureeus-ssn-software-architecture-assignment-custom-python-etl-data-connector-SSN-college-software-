const mongoose = require("mongoose");

const uri = "mongodb://127.0.0.1:27017/mytestdb";

async function testMongo() {
  try {
    await mongoose.connect(uri);
    console.log("✅ Connected to MongoDB successfully!");

    const testSchema = new mongoose.Schema({ name: String, age: Number });
    const Test = mongoose.model("Test", testSchema);

    await mongoose.connection.close();
    console.log("🛑 Connection closed.");
  } catch (err) {
    console.error("❌ MongoDB error:", err);
  }
}

testMongo();
