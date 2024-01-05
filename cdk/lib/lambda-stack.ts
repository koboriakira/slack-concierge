/** @format */

import * as cdk from "@aws-cdk/core";
import * as lambda from "@aws-cdk/aws-lambda";
import * as iam from "@aws-cdk/aws-iam";
import * as apigatewayv2 from "@aws-cdk/aws-apigatewayv2";
import * as apigatewayv2integrations from "@aws-cdk/aws-apigatewayv2-integrations";

export class LambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

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

    // Lambda レイヤーの定義
    const myLayer = new lambda.LayerVersion(this, "MyLayer", {
      // pip install -r requirements.txt -t layer で指定ディレクトリにライブラリをインストール
      code: lambda.Code.fromAsset("../layer"), // レイヤーの内容を含むディレクトリ
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_9], // このレイヤーが互換性を持つランタイム
      description: "A layer for my lambda functions",
      license: "Apache-2.0",
    });

    // Lambda 関数を定義
    const myFunction = new lambda.Function(this, "HelloLambda", {
      runtime: lambda.Runtime.PYTHON_3_9, // ランタイムを指定
      code: lambda.Code.fromAsset("../slack_concierge"), // コードのディレクトリ
      handler: "concierge.handler", // ハンドラーのファイル名とメソッド
      role: role, // Lambdaの実行ロール
      layers: [myLayer], // Lambdaレイヤー
    });

    myFunction.addEnvironment(
      "SLACK_SIGNING_SECRET",
      process.env.SLACK_SIGNING_SECRET || ""
    );
    myFunction.addEnvironment(
      "SLACK_BOT_TOKEN",
      process.env.SLACK_BOT_TOKEN || ""
    );

    // HTTP API の定義
    const httpApi = new apigatewayv2.HttpApi(this, "SlackEventsApi");

    // ルートとインテグレーションの設定
    httpApi.addRoutes({
      path: "/slack/events",
      methods: [apigatewayv2.HttpMethod.POST],
      integration: new apigatewayv2integrations.HttpLambdaIntegration(
        "SlackEventsIntegration",
        myFunction
      ),
    });
  }
}
