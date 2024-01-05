#!/usr/bin/env node
/** @format */

import * as cdk from "@aws-cdk/core";
import { LambdaStack } from "../lib/lambda-stack";

const app = new cdk.App();
new LambdaStack(app, "SlackConciergeLambdaStack");
