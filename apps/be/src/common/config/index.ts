/*
what: 위 설정들을 한 번에 export.
why: CommonModule에서 손쉽게 import하도록.
*/

import appConfig from "./app.config";
import corsConfig from "./cors.config";
import versioningConfig from "./versioning.config";
import securityConfig from "./security.config";

export default [appConfig, corsConfig, versioningConfig, securityConfig];

export { appConfig, corsConfig, versioningConfig, securityConfig };
