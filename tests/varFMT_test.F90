program test

  character(len=40) :: argname
  integer          :: SIZE = 10
  real :: fval(20)
  integer i
  CHARACTER(LEN=30) :: FFMT

  WRITE(FFMT,'("(A20,",I0,"F10.4)")') SIZE

  call random_number(fval)
  do i=1,20
    fval(i) = fval(i) * i
  end do

  argname='some-field'

  ! Works
  write(*,FFMT) trim(argname)//': ', fval(1:SIZE)
  write(*,*)


  ! Outputs some garbage     
  write(*,'(A20,F10.4)', advance='no') trim(argname)//': ', fval(1:SIZE)
  write(*,*)


  ! Is not on oneline
  write(*,'(A20)',advance='no') trim(argname)//': '
  write(*,'(F10.4)',advance='no') fval(1:SIZE)
  write(*,*)
  write(*,*)


  ! Works
  write(*,'(A20)',advance='no') trim(argname)//': '
  do i=1,SIZE
    write(*,'(F10.4)',advance='no') fval(i)    
  end do
  write(*,*)
  write(*,*)

end

