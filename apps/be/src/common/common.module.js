"use strict";
/*
what: 위 설정/컴포넌트들을 한 모듈에 묶어서 전역(Global)제공.
앱 부트스트랩 단계에서 CORS/버전닝/보안헤더 적용,
전역 파이프/필터/인터셉터를 등록하도록 팩토리/프로바이더로 노출.
why: 앱 시작 시점에 공통 정책을 일괄 등록하여, 다른 모듈이 자동 혜택.
*/
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.CommonModule = void 0;
const common_1 = require("@nestjs/common");
const config_1 = require("@nestjs/config");
const config_2 = __importDefault(require("./config"));
const common_2 = require("@nestjs/common");
let CommonModule = class CommonModule {
};
exports.CommonModule = CommonModule;
exports.CommonModule = CommonModule = __decorate([
    (0, common_2.Global)(),
    (0, common_1.Module)({
        imports: [
            config_1.ConfigModule.forRoot({
                isGlobal: true,
                envFilePath: ".env",
                load: config_2.default,
            }),
        ],
        exports: [config_1.ConfigModule],
    })
], CommonModule);
