// import { Injectable, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
// import { PrismaClient } from "@prisma/client";

// @Injectable()
// export class PrismaService
//   extends PrismaClient
//   implements OnModuleInit, OnModuleDestroy
// {
//   // Nest application 시작될 때 DB 연결
//   async onModuleInit() {
//     await this.$connect();
//   }
//   // Nest application 종료될 때 DB 연결 끊기다
//   async onModuleDestroy() {
//     await this.$disconnect();
//   }
// }

import { Injectable, OnModuleInit, OnModuleDestroy } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  async onModuleInit() {
    await this.$connect();
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
