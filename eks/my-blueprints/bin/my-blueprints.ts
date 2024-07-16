#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import * as blueprints from '@aws-quickstart/eks-blueprints';
import { EksBlueprintsVpcStack } from '../lib/eks-blueprints-vpc-stack';
import { KubernetesVersion } from 'aws-cdk-lib/aws-eks';

const app = new cdk.App();
const account = process.env.CDK_DEFAULT_ACCOUNT;
const region = 'ap-northeast-2';
const version = KubernetesVersion.V1_30;

const vpcStack = new EksBlueprintsVpcStack(app, 'eks-blueprint-vpc', {
    env: {
        account: account,
        region: region,
    },
});

blueprints.HelmAddOn.validateHelmVersions = true;

const addOns: Array<blueprints.ClusterAddOn> = [
    new blueprints.addons.ArgoCDAddOn(),
    new blueprints.addons.MetricsServerAddOn(),
    new blueprints.addons.AwsLoadBalancerControllerAddOn(),
    new blueprints.addons.VpcCniAddOn(),
    new blueprints.addons.CoreDnsAddOn(),
    new blueprints.addons.KubeProxyAddOn()
];

blueprints.EksBlueprint.builder()
    .resourceProvider(blueprints.GlobalResources.Vpc, new blueprints.DirectVpcProvider(vpcStack.vpc))
    .account(account)
    .region(region)
    .version(version)
    .addOns(...addOns)
    .useDefaultSecretEncryption(true)
    .build(app, 'eks-blueprints-cluster');
