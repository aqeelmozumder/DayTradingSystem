rs.initiate(
   {
      _id: "shard1",
      version: 1,
      members: [
         { _id: 0, host: "shard1_1:27017" },
         { _id: 1, host: "shard1_2:27017" },
         { _id: 2, host: "shard1_3:27017" }
      ]
   }
)
