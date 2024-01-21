#!/usr/bin/env node
/** @format */

import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { SlackConcierge } from "../lib/slack-concierge";

const app = new cdk.App();
new SlackConcierge(app, "SlackConcierge", {});
