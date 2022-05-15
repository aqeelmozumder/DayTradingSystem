rs.initiate(
   {
      _id: "shard2",
      version: 1,
      members: [
         { _id: 0, host: "shard2_1:27017" },
         { _id: 1, host: "shard2_2:27017" },
         { _id: 2, host: "shard2_3:27017" }
      ]
   }
)
