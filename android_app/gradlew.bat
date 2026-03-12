@rem
@rem Copyright 2015 the original author or authors.
@rem
@rem Licensed under the Apache License, Version 2.0 (the "License");
@rem you may not use this file except in compliance with the License.
@rem You may obtain a copy of the License at
@rem
@rem      https://www.apache.org/licenses/LICENSE-2.0
@rem
@rem Unless required by applicable law or agreed to in writing, software
@rem distributed under the License is distributed on an "AS IS" BASIS,
@rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
@rem See the License for the specific language governing permissions and
@rem limitations under the License.
@rem

@if "%DEBUG%"=="" @echo off

set APP_HOME=%~dp0
set CLASSPATH=%APP_HOME%gradle\wrapper\gradle-wrapper.jar

if not exist "%CLASSPATH%" (
  echo.
  echo ERROR: gradle-wrapper.jar not found. Run the following once (requires Gradle installed):
  echo   gradle wrapper --gradle-version 9.0.0
  echo.
  echo Or install Gradle: https://gradle.org/install/
  echo On macOS: brew install gradle
  echo.
  exit /b 1
)

exec "%JAVA_HOME%\bin\java" -Dorg.gradle.appname=GradleWrapper -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
