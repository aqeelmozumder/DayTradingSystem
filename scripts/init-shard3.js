rs.initiate(
   {
      _id: "shard3",
      version: 1,
      members: [
         { _id: 0, host: "shard3_1:27017" },
         { _id: 1, host: "shard3_2:27017" },
         { _id: 2, host: "shard3_3:27017" }
      ]
   }
)
