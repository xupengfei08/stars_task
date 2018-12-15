db = db.getSiblingDB('stars_task');  // 创建一个名为"stars_task"的DB
db.createUser(  // 创建一个名为"root"的用户，设置密码和权限
    {
        user: "root",
        pwd: "123456",
        roles: [
            { role: "dbOwner", db: "stars_task"}
        ]
    }
);
db.createCollection("user");  // 在"stars_task"中创建一个名为"user"的Collection