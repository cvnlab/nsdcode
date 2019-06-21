function f = cvnmapsurfacetovolume_helper(data,vertices,res,specialmode,emptyval)

% function f = cvnmapsurfacetovolume_helper(data,vertices,res,specialmode,emptyval)
%
% <data> is the data with dimensionality D (datasets) x V (vertices).
% <vertices> is 3 x V with the X-, Y-, and Z- coordinates of the vertices.
% <res> is the desired volume size. For example, 256 means 256 x 256 x 256.
% <specialmode> is 0 means usual linear weighting; 1 means treat each dataset as
%   consisting of discrete integer labels and perform a winner-take-all voting mechanism.
% <emptyval> is the value to use when no vertices map to a voxel
%
% return the data mapped to a volume in <f>.
% <f> has dimensionality <res> x <res> x <res> x D.
% we automatically convert <data> to double and return output as double.

% calc/define
m = size(vertices,2);   % number of vertices
n = res^3;              % number of voxels
d = size(data,1);       % number of distinct datasets

% ensure double
data = double(data);

% prepare some sparse-related stuff
AA = 1:m;

% construct X [vertices x voxels, each row has 8 entries with weights, the max for a weight is 3]
Xold = sparse(m,n);
for x=[-1 1]
  for y=[-1 1]
    for z=[-1 1]
    
      % calc the voxel index and the distance away from that voxel index
      if x==1
        xR = ceil(vertices(1,:));    % ceil-val  (.1 means use weight of .9)
        xD = xR-vertices(1,:);       
      else
        xR = floor(vertices(1,:));   % val-floor (.1 means use weight of .9)
        xD = vertices(1,:)-xR;
      end

      if y==1
        yR = ceil(vertices(2,:));
        yD = yR-vertices(2,:);
      else
        yR = floor(vertices(2,:));
        yD = vertices(2,:)-yR;
      end

      if z==1
        zR = ceil(vertices(3,:));
        zD = zR-vertices(3,:);
      else
        zR = floor(vertices(3,:));
        zD = vertices(3,:)-zR;
      end
      
      % calc
      II = sub2ind([res res res],xR,yR,zR);  % 1 x vertices with the voxel index to go to
      DD = (1-xD)+(1-yD)+(1-zD);             % 1 x vertices with the weight to assign
      
      % construct the entries and add the old one in
      X = sparse(AA,II,DD,m,n);
      X = Xold + X;
      Xold = X;

    end
  end
end
clear Xold;

% do it
if specialmode==0

  % each voxel is assigned a weighted sum of vertex values.
  % this should be done as a weighted average. thus, need to divide by sum of weights.
  % let's compute that now.
  wtssum = ones(1,m)*X;  % 1 x voxels

  % take the vertex data and map to voxels
  f = data*X;      % d x voxels

  % do the normalization [if a voxel has no vertex contribution, it gets <emptyval>]
  f = zerodiv(f,repmat(wtssum,[d 1]),emptyval);

  % prepare the results
  f = reshape(f',[res res res d]);

else

  % loop over datasets
  f = [];
  for q=1:d
    
    % figure out discrete integer labels
    alllabels = flatten(union(data(q,:),[]));
    assert(all(isfinite(alllabels)));
    
    % expand data into separate channels
    datanew = zeros(length(alllabels),size(data,2));  % N x vertices
    for p=1:length(alllabels)
      datanew(p,:) = double(data(q,:)==alllabels(p));
    end
    
    % take the vertex data and map to voxels
    f0 = datanew*X;      % N x voxels
  
    % which voxels have no vertex contribution?
    bad = sum(f0,1)==0;
  
    % perform winner-take-all (f0 is the index relative to alllabels!)
    [mx,f0] = max(f0,[],1);
  
    % figure out the final labeling scheme
    finaldata = alllabels(f0);
  
    % put in <emptyval>
    finaldata(bad) = emptyval;
    
    % save
    f(:,:,:,q) = reshape(finaldata,[res res res]);

  end

end
