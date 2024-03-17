/** @format */

import {
  Stack,
  StackProps,
  Duration,
  aws_lambda as lambda,
  aws_iam as iam,
  aws_events as events,
  aws_events_targets as targets,
  aws_sqs as sqs,
  aws_apigateway as apigateway,
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

    // slack-concierge-api: FastAPIを使ったAPI Gateway
    const fn = this.createLambdaFunction(
      "FastapiMain",
      role,
      myLayer,
      "fastapi_main.handler",
      30,
      true
    );

    // REST API
    const restapi = new apigateway.RestApi(this, "Notion-Api", {
      deployOptions: {
        stageName: "v1",
      },
      restApiName: "Slack-Concierge-Api",
    });
    restapi.root.addMethod("ANY", new apigateway.LambdaIntegration(fn));
    restapi.root
      .addResource("{proxy+}")
      .addMethod("ANY", new apigateway.LambdaIntegration(fn));

    // lazy_main: SlackBoltを使ったLambda関数
    const lambda_lazy_main = this.createLambdaFunction(
      "Lambda",
      role,
      myLayer,
      "lazy_main.handler",
      30,
      true
    );

    this.createLambdaFunctionScheduler(role, myLayer);

    const lambda_notificate_schedule = this.createEventLambda(
      "NotificateSchedule",
      role,
      myLayer,
      "notificate_schedule.handler",
      // JSTで、AM6:00からPM11:00までの間、5分おきに実行
      // see https://docs.aws.amazon.com/ja_jp/AmazonCloudWatch/latest/events/ScheduledEvents.html#CronExpressions
      events.Schedule.cron({ minute: "*/5", hour: "21-14" })
    );

    const syncScheduleToTask = this.createEventLambda(
      "SyncScheduleToTask",
      role,
      myLayer,
      "sync_schedule_to_task.handler",
      // JSTで、PM9:00に実行
      events.Schedule.cron({ minute: "0", hour: "12" })
    );

    // complete_task: SQSから呼び出される
    const remindToRecordAchivement = this.createEventLambda(
      "RemindToRecordAchivement",
      role,
      myLayer,
      "remind_to_record_achivement.handler",
      // JSTで、AM9:00からPM10:55までの間、5分おきに実行
      events.Schedule.cron({ minute: "*/5", hour: "0-13" })
    );

    const listTodayTasks = this.createEventLambda(
      "ListTodayTasks",
      role,
      myLayer,
      "list_today_tasks.handler",
      // JSTで、AM7:00に実行
      events.Schedule.cron({ minute: "0", hour: "22" })
    );

    // love_spotify_track: SQSから呼び出される
    const loveSpotifyTrack = this.createLambdaAndSqs(
      "LoveSpotifyTrack",
      role,
      myLayer,
      "love_spotify_track.handler",
      lambda_lazy_main
    );

    // complete_task: SQSから呼び出される
    const completeTask = this.createLambdaAndSqs(
      "CompleteTask",
      role,
      myLayer,
      "complete_task.handler",
      lambda_lazy_main
    );


    // test
    const test = this.createLambdaFunction(
      "Test",
      role,
      myLayer,
      "test_handler.handler"
    );
  }

  /**
   * 任意に作成されるEventBridgeSchedulerで実行されるLambda関数を作成
   * @param role
   * @param myLayer
   */
  createLambdaFunctionScheduler(
    roleForLambda: iam.Role,
    myLayer: lambda.LayerVersion
  ) {
    const scheduleExecutionRole = new iam.Role(this, "ScheduleExecutionRole", {
      assumedBy: new iam.ServicePrincipal("scheduler.amazonaws.com"),
    });

    const pomodoroTimer = this.createLambdaFunction(
      "PomodoroTimer",
      roleForLambda,
      myLayer,
      "pomodoro_timer.handler"
    );
    scheduleExecutionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:InvokeFunction"],
        resources: [
          pomodoroTimer.functionArn,
          pomodoroTimer.functionArn + ":*",
        ],
      })
    );

    const createTask = this.createLambdaFunction(
      "CreateTask",
      roleForLambda,
      myLayer,
      "create_task.handler"
    );
    scheduleExecutionRole.addToPolicy(
      new iam.PolicyStatement({
        actions: ["lambda:InvokeFunction"],
        resources: [createTask.functionArn, createTask.functionArn + ":*"],
      })
    );
  }

  createEventLambda(
    name: string,
    role: iam.Role,
    myLayer: lambda.LayerVersion,
    handler: string,
    schedule: events.Schedule,
    timeout: number = 60
  ) {
    const fn = this.createLambdaFunction(
      name,
      role,
      myLayer,
      handler,
      timeout,
      false
    );
    new events.Rule(this, name + "Rule", {
      schedule: schedule,
      targets: [
        new targets.LambdaFunction(fn, {
          retryAttempts: 0,
        }),
      ],
    });
  }

  createLambdaAndSqs(
    name: string,
    role: iam.Role,
    myLayer: lambda.LayerVersion,
    handler: string,
    lambda_lazy_main: lambda.Function,
    timeout: number = 30
  ) {
    const functionForSqs = this.createLambdaFunction(
      name,
      role,
      myLayer,
      handler,
      timeout,
      false
    );
    const queue = new sqs.Queue(this, name + "Queue", {
      visibilityTimeout: Duration.seconds(300),
    });
    queue.grantConsumeMessages(functionForSqs);
    queue.grantSendMessages(lambda_lazy_main);
    functionForSqs.addEventSourceMapping(name + "EventSource", {
      eventSourceArn: queue.queueArn,
      batchSize: 1,
    });
    return functionForSqs;
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
    // スケジューラを作成するために必要な権限
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["scheduler:*", "events:*"],
        resources: ["*"],
      })
    );
    // スケジューラを作成するために必要な権限（CreateScheduleするときにiam:PassRoleが必要らしい）
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["iam:PassRole"],
        resources: ["*"],
      })
    );
    // SQSにメッセージを送信するために必要な権限
    role.addToPrincipalPolicy(
      new iam.PolicyStatement({
        actions: ["sqs:sendMessage"],
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
    timeout: number = 60,
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
