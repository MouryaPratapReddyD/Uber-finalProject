#
# EKS Cluster Resources
#  * EC2 Security Group to allow networking traffic with EKS cluster
#

resource "aws_security_group" "final-cluster" {
  name        = "terraform-eks-final-cluster"
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.final.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "terraform-eks-final"
  }
}

resource "aws_security_group_rule" "final-cluster-ingress-node-https" {
  description              = "Allow pods to communicate with the cluster API Server"
  from_port                = 443
  protocol                 = "tcp"
  security_group_id        = "${aws_security_group.final-cluster.id}"
  source_security_group_id = "${aws_security_group.final-node.id}"
  to_port                  = 443
  type                     = "ingress"
}

resource "aws_security_group_rule" "final-cluster-ingress-workstation-https" {
  cidr_blocks       = ["0.0.0.0/0"]
  description       = "Allow workstation to communicate with the cluster API Server"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = "${aws_security_group.final-cluster.id}"
  to_port           = 443
  type              = "ingress"
}