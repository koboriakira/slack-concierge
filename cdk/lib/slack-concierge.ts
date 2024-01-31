/** @format */

import {
  Stack,
  StackProps,
  Duration,
  aws_lambda as lambda,
  aws_iam as iam,
  aws_events as events,
  aws_events_targets as targets,
} from "aws-cdk-lib";
import { Construct } from "constructs";

// CONFIG
const RUNTIME = lambda.Runtime.PYTHON_3_11;
const APP_DIR_PATH = "../slack";
const LAYER_ZIP_PATH = "../dependencies.zip";

export class SlackConcierge extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const role = this.makeRole();
    const myLayer = this.makeLayer();

    // lazy_main
    const lambda_lazy_main = this.createLambdaFunction(
      "Lambda",
      role,
      myLayer,
      "lazy_main.handler",
      30,
      true
    );

    // pomodoro_timer
    const pomodoroTimer = this.createLambdaFunction(
      "PomodoroTimer",
      role,
      myLayer,
      "pomodoro_timer.handler",
      15,
      false
    );

    // notificate_schedule
    const lambda_notificate_schedule = this.createLambdaFunction(
      "NotificateSchedule",
      role,
      myLayer,
      "notificate_schedule.handler",
      60,
      false
    );
    // notificate_schedule: EventBridgeのルール
    new events.Rule(this, "NotificateScheduleRule", {
      // JSTで、AM6:00からPM11:00までの間、5分おきに実行
      // see https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions
      schedule: events.Schedule.cron({ minute: "*/5", hour: "21-14" }),
      targets: [
        new targets.LambdaFunction(lambda_notificate_schedule, {
          retryAttempts: 0,
        }),
      ],
    });
  }

  /**
   * Create or retrieve an IAM role for the Lambda function.
   * @returns {iam.Role} The created or retrieved IAM role.
   */
  makeRole() {
    // Lambdaの実行ロールを取得または新規作成
    const role = new iam.Role(this, "LambdaRole", {
      assumedBy: new iam.ServicePrincipal("lambda.amazonaws.com"),
    });

    // Lambda の実行ロールに管理ポリシーを追加
    role.addManagedPolicy(
      iam.ManagedPolicy.fromAwsManagedPolicyName(
        "service-role/AWSLambdaBasicExecutionRole"
      )
    );

    // 必要に応じて追加の権限をポリシーとしてロールに付与
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:InvokeFunction", "lambda:InvokeAsync"],
        resources: ["*"],
      })
    );
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ["s3:*"],
        resources: [
          "arn:aws:s3:::koboriakira-bucket",
          "arn:aws:s3:::koboriakira-bucket/*",
        ],
      })
    );
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["scheduler:*", "events:*"],
        resources: ["*"],
      })
    );

    return role;
  }

  /**
   * Create or retrieve a Lambda layer.
   * @returns {lambda.LayerVersion} The created or retrieved Lambda layer.
   */
  makeLayer() {
    return new lambda.LayerVersion(this, "Layer", {
      code: lambda.Code.fromAsset(LAYER_ZIP_PATH), // レイヤーの内容を含むディレクトリ
      compatibleRuntimes: [RUNTIME], // このレイヤーが互換性を持つランタイム
    });
  }

  /**
   * Create a Lambda function.
   * @param {iam.Role} role The IAM role for the Lambda function.
   * @param {lambda.LayerVersion} myLayer The Lambda layer to be used.
   * @returns {lambda.Function} The created Lambda function.
   */
  createLambdaFunction(
    name: string,
    role: iam.Role,
    myLayer: lambda.LayerVersion,
    handler: string,
    timeout: number = 30,
    function_url_enabled: boolean = false
  ): lambda.Function {
    const fn = new lambda.Function(this, name, {
      runtime: RUNTIME,
      handler: handler,
      code: lambda.Code.fromAsset(APP_DIR_PATH),
      role: role,
      layers: [myLayer],
      timeout: Duration.seconds(timeout),
      retryAttempts: 0,
    });

    fn.addEnvironment(
      "SLACK_SIGNING_SECRET",
      process.env.SLACK_SIGNING_SECRET || ""
    );
    fn.addEnvironment("SLACK_BOT_TOKEN", process.env.SLACK_BOT_TOKEN || "");
    fn.addEnvironment(
      "LAMBDA_GOOGLE_CALENDAR_API_DOMAIN",
      process.env.LAMBDA_GOOGLE_CALENDAR_API_DOMAIN || ""
    );
    fn.addEnvironment("GAS_DEPLOY_ID", process.env.GAS_DEPLOY_ID || "");
    fn.addEnvironment(
      "LAMBDA_NOTION_API_DOMAIN",
      process.env.LAMBDA_NOTION_API_DOMAIN || ""
    );
    fn.addEnvironment("NOTION_SECRET", process.env.NOTION_SECRET || "");
    fn.addEnvironment(
      "BUSINESS_SLACK_USER_TOKEN",
      process.env.BUSINESS_SLACK_USER_TOKEN || ""
    );
    fn.addEnvironment("SLACK_USER_TOKEN", process.env.SLACK_USER_TOKEN || "");
    fn.addEnvironment(
      "SPOTIFY_CLIENT_SECRET",
      process.env.SPOTIFY_CLIENT_SECRET || ""
    );
    fn.addEnvironment("OPENAI_API_KEY", process.env.OPENAI_API_KEY || "");
    fn.addEnvironment("AWS_ACCOUNT_ID", process.env.AWS_ACCOUNT_ID || "");

    if (function_url_enabled) {
      fn.addFunctionUrl({
        authType: lambda.FunctionUrlAuthType.NONE, // 認証なし
      });
    }

    return fn;
  }
}
