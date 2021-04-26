#
# EKS Cluster Resources
#  * EKS Cluster
#
#  It can take a few minutes to provision on AWS

# Note: replace subnet_ids = ["${aws_subnet.final.*.id}"]
# with:
# subnet_ids = flatten([aws_subnet.final.0.id, aws_subnet.final.1.id])
# or:
# subnet_ids = "${aws_subnet.final.*.id}"

resource "aws_eks_cluster" "final" {
  name     = var.cluster-name
  role_arn = aws_iam_role.final-cluster.arn

vpc_config {
   security_group_ids = ["${aws_security_group.final-cluster.id}"]
   subnet_ids         = aws_subnet.final.*.id
 }

  depends_on = [
    aws_iam_role_policy_attachment.final-cluster-AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.final-cluster-AmazonEKSServicePolicy,
  ]
}
