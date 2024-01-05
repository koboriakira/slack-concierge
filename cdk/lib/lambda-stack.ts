/** @format */

import * as cdk from "@aws-cdk/core";
import * as lambda from "@aws-cdk/aws-lambda";

export class LambdaStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Lambda 関数を定義
    const helloLambda = new lambda.Function(this, "HelloLambda", {
      runtime: lambda.Runtime.PYTHON_3_9, // ランタイムを指定
      code: lambda.Code.fromAsset("../slack_concierge"), // コードのディレクトリ
      handler: "concierge.handler", // ハンドラーのファイル名とメソッド
    });
  }
}
