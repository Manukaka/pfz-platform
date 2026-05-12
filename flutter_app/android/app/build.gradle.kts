import java.util.Properties

plugins {
    id("com.android.application")
    id("kotlin-android")
    id("com.google.gms.google-services")
    id("dev.flutter.flutter-gradle-plugin")
}

// Read local.properties for tokens
val localProperties = Properties()
val localPropertiesFile = rootProject.file("local.properties")
if (localPropertiesFile.exists()) {
    localPropertiesFile.inputStream().use { localProperties.load(it) }
}

val mapboxToken: String = (localProperties.getProperty("MAPBOX_ACCESS_TOKEN")
    ?: System.getenv("MAPBOX_ACCESS_TOKEN")
    ?: "").ifBlank { "pk.placeholder_debug_no_maps" }

android {
    namespace = "com.daryasagar.darya_sagar"
    compileSdk = flutter.compileSdkVersion
    ndkVersion = flutter.ndkVersion

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_17.toString()
    }

    defaultConfig {
        applicationId = "com.daryasagar.darya_sagar"
        minSdk = 24  // Required by Mapbox Maps v11
        targetSdk = flutter.targetSdkVersion
        versionCode = flutter.versionCode
        versionName = flutter.versionName

        // Inject Mapbox token into manifest placeholder
        manifestPlaceholders["MAPBOX_ACCESS_TOKEN"] = mapboxToken

        // Enable multidex (large app)
        multiDexEnabled = true
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("debug")
            isMinifyEnabled = false
            isShrinkResources = false
        }
        debug {
            manifestPlaceholders["MAPBOX_ACCESS_TOKEN"] = mapboxToken
        }
    }
}

flutter {
    source = "../.."
}
