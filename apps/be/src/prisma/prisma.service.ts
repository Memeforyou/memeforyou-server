import { Injectable, OnModuleDestroy, OnModuleInit } from "@nestjs/common";
import { PrismaClient } from "@prisma/client";

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  // Nest application 시작될 때 DB 연결
  async onModuleInit() {
    await this.$connect();
  }
  // Nest application 종료될 때 DB 연결 끊기
  async onModuleDestroy() {
    await this.$disconnect();
  }
}
