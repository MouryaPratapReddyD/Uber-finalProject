# usage of the specific kubernetes.io/cluster/* resource tag is required for 
# EKS and Kubernetes to discover and manage compute resources

# Note:
# vpc_zone_identifier  = ["${aws_subnet.final.*.id}"]
# was replaced with:
# vpc_zone_identifier  = "${aws_subnet.final.*.id}"

resource "aws_autoscaling_group" "final" {
  desired_capacity     = 4
  launch_configuration = "${aws_launch_configuration.final.id}"
  max_size             = 4
  min_size             = 1
  name                 = "terraform-eks-final"
  vpc_zone_identifier  = aws_subnet.final.*.id

  tag {
    key                 = "Name"
    value               = "terraform-eks-final"
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.cluster-name}"
    value               = "owned"
    propagate_at_launch = true
  }
}
