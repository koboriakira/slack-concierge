/** @format */

import {
  Stack,
  StackProps,
  Duration,
  aws_lambda as lambda,
  aws_iam as iam,
  aws_apigateway as apigateway,
} from "aws-cdk-lib";
import { Construct } from "constructs";

// CONFIG
const RUNTIME = lambda.Runtime.PYTHON_3_11;
const TIMEOUT = 30;
const APP_DIR_PATH = "../slack";
const HANDLER_NAME = "lazy_main.handler";
const LAYER_ZIP_PATH = "../dependencies.zip";

export class SlackConcierge extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const role = this.makeRole();
    const myLayer = this.makeLayer();
    const fn = this.createLambdaFunction(role, myLayer);
    this.makeApiGateway(fn);
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
    role: iam.Role,
    myLayer: lambda.LayerVersion
  ): lambda.Function {
    const fn = new lambda.Function(this, "Lambda", {
      runtime: RUNTIME,
      handler: HANDLER_NAME,
      code: lambda.Code.fromAsset(APP_DIR_PATH),
      role: role,
      layers: [myLayer],
      timeout: Duration.seconds(TIMEOUT),
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

    fn.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE, // 認証なし
    });

    return fn;
  }

  /**
   * Create an API Gateway.
   * @param {lambda.Function} fn The Lambda function to be integrated.
   */
  makeApiGateway(fn: lambda.Function) {
    // REST API の定義
    const restapi = new apigateway.RestApi(this, "Slack-Concierge", {
      deployOptions: {
        stageName: "v1",
      },
      restApiName: "Slack-Concierge",
    });
    // ルートとインテグレーションの設定
    restapi.root.addMethod("ANY", new apigateway.LambdaIntegration(fn));
    restapi.root
      .addResource("{proxy+}")
      .addMethod("GET", new apigateway.LambdaIntegration(fn));
    return restapi;
  }
}
